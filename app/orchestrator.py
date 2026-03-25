from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from app.adapters import (
    bundesportal,
    berlin_service,
    nrw_service,
    elster,
    dguv,
    geoportal,
)
from app.agent import AppDeps, legal_agent
from app.pipelines.rules import derive_flags
from app.schemas import ActionStep, CaseProfile, CaseResult, Procedure, RiskFlag

logger = logging.getLogger(__name__)


def gather_procedures(
    case: CaseProfile,
) -> tuple[list[Procedure], list[ActionStep], list[RiskFlag]]:
    """Call adapters based on derived flags. Returns raw data, no agent involved."""
    flags = derive_flags(case)
    procedures: list[Procedure] = []
    action_steps: list[ActionStep] = []
    risk_flags: list[RiskFlag] = []

    state_val = case.state.value

    # Always: trade registration
    if state_val == "Berlin":
        procedures.append(bundesportal.get_trade_registration(state_val, case.city))
    else:
        procedures.append(nrw_service.get_business_registration(state_val, case.city))

    # Always: food business registration
    procedures.append(
        bundesportal.get_food_business_registration(state_val, case.city)
    )

    # Conditional: IfSG
    if flags.needs_ifsg:
        procedures.append(bundesportal.get_ifsg_instruction(state_val, case.city))

    # Conditional: restaurant permit
    if flags.needs_restaurant_permit:
        if state_val == "Berlin":
            procedures.append(
                berlin_service.get_restaurant_permit(state_val, case.city, True)
            )
        else:  # NRW
            procedures.append(
                nrw_service.get_restaurant_permit(state_val, case.city, True)
            )
    else:
        # Still document the non-requirement
        if state_val == "Berlin":
            procedures.append(
                berlin_service.get_restaurant_permit(state_val, case.city, False)
            )
        else:  # NRW
            procedures.append(
                nrw_service.get_restaurant_permit(state_val, case.city, False)
            )

    # Conditional: IHK Unterrichtung (decoupled from restaurant permit flag)
    if flags.needs_ihk_instruction and state_val == "Berlin":
        procedures.append(
            berlin_service.get_ihk_instruction(state_val, case.city, True)
        )

    # Always: tax registration
    action_steps.append(elster.get_tax_registration_step(case.legal_form))

    # Always: DGUV (when employees exist, implicit for food businesses)
    action_steps.append(dguv.get_dguv_registration_step())

    # Conditional: location risk
    if flags.needs_location_followup:
        risk_flags.extend(geoportal.flag_location_risk(existing_gastro_premises=False))
    else:
        risk_flags.extend(geoportal.flag_location_risk(existing_gastro_premises=True))

    return procedures, action_steps, risk_flags


def build_checklist(
    case: CaseProfile, procedures: list[Procedure], action_steps: list[ActionStep]
) -> CaseResult:
    """Build the rule-based checklist from gathered procedures and action steps."""
    flags = derive_flags(case)
    must_do: list[str] = []
    conditional: list[str] = []
    documents: list[str] = []
    authorities: list[str] = []
    links: list[str] = []

    for proc in procedures:
        if proc.category == "trade":
            must_do.append(f"Register trade (Gewerbeanmeldung) in {case.city}")
            if proc.source_url:
                links.append(proc.source_url)
            authorities.append("Gewerbeamt (Trade Office)")
        elif proc.category == "food":
            must_do.append(
                "Register food business with veterinary/food supervision office"
            )
            if proc.source_url:
                links.append(proc.source_url)
            authorities.append("Veterinär- und Lebensmittelaufsicht")
        elif proc.category == "health":
            must_do.append("Complete IfSG instruction for all food-handling staff")
            if proc.source_url:
                links.append(proc.source_url)
            authorities.append("Gesundheitsamt (Health Office)")
        elif proc.category == "permit":
            if flags.needs_restaurant_permit:
                conditional.append(
                    f"Apply for Gaststättenerlaubnis (Restaurant Permit) in {case.state}"
                )
                documents.append("Führungszeugnis (Police Clearance)")
                documents.append("Gewerbezentralauszug (Trade Register Extract)")
                if proc.source_url:
                    links.append(proc.source_url)
                authorities.append("Ordnungsamt (Public Order Office)")
        elif proc.category == "instruction":
            if flags.needs_ihk_instruction and proc.steps:
                conditional.append(
                    "Complete IHK Unterrichtung (gastronomy instruction)"
                )
                if proc.source_url:
                    links.append(proc.source_url)
                authorities.append("IHK")

    if flags.needs_commercial_register:
        must_do.append(
            "Register with Handelsregister (commercial register) before Gewerbeanmeldung"
        )
        authorities.append("Amtsgericht (Local Court)")

    for step in action_steps:
        if step.action_type == "registration":
            must_do.append(step.title)
        elif step.action_type == "insurance":
            must_do.append(step.title)
        if step.source_url:
            links.append(step.source_url)
        if step.action_url:
            links.append(step.action_url)

    return CaseResult(
        must_do_now=must_do,
        conditional_steps=conditional,
        documents=documents,
        authorities=list(dict.fromkeys(authorities)),
        official_links=list(dict.fromkeys(links)),
        procedures=procedures,
        action_steps=action_steps,
        flags=flags,
        generated_at=datetime.now(tz=UTC).isoformat(),
    )


async def evaluate_case(case: CaseProfile) -> CaseResult:
    """Full orchestrator: validate → rules → adapters → merge → agent summary."""
    procedures, action_steps, risk_flags = gather_procedures(case)
    result = build_checklist(case, procedures, action_steps)
    result.risk_flags = risk_flags
    result.stale_cache_warnings = [p.title for p in procedures if p.cache_stale]

    # Ask the LLM agent for summary + open questions
    context_text = _format_context(case, result)
    async with httpx.AsyncClient() as client:
        deps = AppDeps(http_client=client)
        try:
            agent_result = await legal_agent.run(
                f"Case: {case.model_dump_json()}\n\n{context_text}",
                deps=deps,
            )
            result.summary = agent_result.output.summary
            result.open_questions = agent_result.output.open_questions
        except Exception as exc:
            logger.error("Agent summary failed: %s", exc)
            result.summary = (
                "Agent summary unavailable. Please review the checklist above."
            )
            result.open_questions = []

    return result


async def gather_procedures_live(
    case: CaseProfile,
) -> tuple[list[Procedure], list[ActionStep], list[RiskFlag]]:
    """Live mode: fetch SDG procedures for NRW; Berlin stays static."""
    from app.adapters.sdg_client import SDGClient

    flags = derive_flags(case)
    procedures: list[Procedure] = []
    action_steps: list[ActionStep] = []
    risk_flags: list[RiskFlag] = []
    state_val = case.state.value

    async with httpx.AsyncClient() as http_client:
        sdg = SDGClient(http_client=http_client)

        # Trade registration
        if state_val == "Berlin":
            procedures.append(
                bundesportal.get_trade_registration(state_val, case.city)
            )
        else:
            trade_proc = await sdg.get_procedure("trade", city=case.city, state=state_val)
            trade_proc.category = "trade"
            procedures.append(trade_proc)

        # Food business registration
        if state_val == "Berlin":
            procedures.append(
                bundesportal.get_food_business_registration(state_val, case.city)
            )
        else:
            food_proc = await sdg.get_procedure("food", city=case.city, state=state_val)
            food_proc.category = "food"
            procedures.append(food_proc)

        # IfSG instruction
        if flags.needs_ifsg:
            if state_val == "Berlin":
                procedures.append(
                    bundesportal.get_ifsg_instruction(state_val, case.city)
                )
            else:
                ifsg_proc = await sdg.get_procedure("ifsg", city=case.city, state=state_val)
                ifsg_proc.category = "health"
                procedures.append(ifsg_proc)

    # Restaurant permit — state-specific static adapters
    if flags.needs_restaurant_permit:
        if state_val == "Berlin":
            procedures.append(
                berlin_service.get_restaurant_permit(state_val, case.city, True)
            )
        else:  # NRW
            procedures.append(
                nrw_service.get_restaurant_permit(state_val, case.city, True)
            )
    else:
        if state_val == "Berlin":
            procedures.append(
                berlin_service.get_restaurant_permit(state_val, case.city, False)
            )
        else:  # NRW
            procedures.append(
                nrw_service.get_restaurant_permit(state_val, case.city, False)
            )

    # Conditional: IHK Unterrichtung (decoupled from restaurant permit flag)
    if flags.needs_ihk_instruction and state_val == "Berlin":
        procedures.append(
            berlin_service.get_ihk_instruction(state_val, case.city, True)
        )

    # Tax + DGUV (always static)
    action_steps.append(elster.get_tax_registration_step(case.legal_form))
    action_steps.append(dguv.get_dguv_registration_step())

    # Location risk
    if flags.needs_location_followup:
        risk_flags.extend(geoportal.flag_location_risk(existing_gastro_premises=False))
    else:
        risk_flags.extend(geoportal.flag_location_risk(existing_gastro_premises=True))

    return procedures, action_steps, risk_flags


async def evaluate_case_live(case: CaseProfile) -> CaseResult:
    """Live orchestrator: SDG for all non-Berlin states, static for Berlin."""
    procedures, action_steps, risk_flags = await gather_procedures_live(case)
    result = build_checklist(case, procedures, action_steps)
    result.risk_flags = risk_flags
    result.stale_cache_warnings = [p.title for p in procedures if p.cache_stale]

    # Ask the LLM agent for summary + open questions
    context_text = _format_context(case, result)
    async with httpx.AsyncClient() as client:
        deps = AppDeps(http_client=client)
        try:
            agent_result = await legal_agent.run(
                f"Case: {case.model_dump_json()}\n\n{context_text}",
                deps=deps,
            )
            result.summary = agent_result.output.summary
            result.open_questions = agent_result.output.open_questions
        except Exception as exc:
            logger.error("Agent summary failed: %s", exc)
            result.summary = (
                "Agent summary unavailable. Please review the checklist above."
            )
            result.open_questions = []

    return result


def _format_context(case: CaseProfile, result: CaseResult) -> str:
    """Format the checklist data for the LLM prompt."""
    lines = ["=== PROCEDURES ==="]
    for p in result.procedures:
        lines.append(f"- {p.title}: {p.description}")
        if p.source_url:
            lines.append(f"  Source: {p.source_url}")

    lines.append("\n=== ACTION STEPS ===")
    for a in result.action_steps:
        lines.append(f"- {a.title}: {a.description}")

    lines.append("\n=== RISK FLAGS ===")
    for r in result.risk_flags:
        lines.append(f"- [{r.severity.upper()}] {r.category}: {r.description}")
        if r.recommendation:
            lines.append(f"  Recommendation: {r.recommendation}")

    lines.append(f"\n=== FLAGS ===")
    for k, v in result.flags.model_dump().items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines)
