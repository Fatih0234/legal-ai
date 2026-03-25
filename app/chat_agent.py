from __future__ import annotations

from pydantic_ai import Agent

from app.agent import AppDeps, build_model
from app.adapters import (
    bundesportal,
    berlin_service,
    nrw_service,
    elster,
    dguv,
    geoportal,
    sozialversicherung,
)
from app.prompts import CHAT_SYSTEM_PROMPT

chat_agent = Agent(
    build_model(),
    deps_type=AppDeps,
    instructions=CHAT_SYSTEM_PROMPT,
    model_settings={"temperature": 0.1},
)


@chat_agent.tool_plain
def get_trade_registration(state: str, city: str) -> str:
    """Get the trade registration (Gewerbeanmeldung) procedure for a given state and city.

    Args:
        state: German state, e.g. "Berlin" or "NRW"
        city: City name, e.g. "Berlin", "Köln", "Düsseldorf"
    """
    if state == "NRW":
        proc = nrw_service.get_business_registration(state, city)
    else:
        proc = bundesportal.get_trade_registration(state, city)
    return proc.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_food_registration(state: str, city: str) -> str:
    """Get the food business registration (Lebensmittelbetrieb registrieren) procedure.

    Args:
        state: German state, e.g. "Berlin" or "NRW"
        city: City name, e.g. "Berlin", "Köln"
    """
    proc = bundesportal.get_food_business_registration(state, city)
    return proc.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_ifsg_instruction(state: str, city: str) -> str:
    """Get the infection protection instruction (Belehrung nach IfSG) procedure.
    Required for all staff handling open food.

    Args:
        state: German state, e.g. "Berlin" or "NRW"
        city: City name, e.g. "Berlin", "Köln"
    """
    proc = bundesportal.get_ifsg_instruction(state, city)
    return proc.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_restaurant_permit(state: str, city: str, serves_alcohol: bool) -> str:
    """Get the restaurant permit (Gaststättenerlaubnis) procedure.
    Only required if serving alcohol.

    Args:
        state: German state, e.g. "Berlin" or "NRW"
        city: City name, e.g. "Berlin", "Köln"
        serves_alcohol: Whether alcohol is served
    """
    if state == "Berlin":
        proc = berlin_service.get_restaurant_permit(state, city, serves_alcohol)
    else:
        proc = nrw_service.get_restaurant_permit(state, city, serves_alcohol)
    return proc.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_ihk_instruction(state: str, city: str, serves_alcohol: bool) -> str:
    """Get the IHK gastronomy instruction (IHK Unterrichtung) procedure.
    Only required if serving alcohol (Berlin).

    Args:
        state: German state, e.g. "Berlin" or "NRW"
        city: City name, e.g. "Berlin", "Köln"
        serves_alcohol: Whether alcohol is served
    """
    proc = berlin_service.get_ihk_instruction(state, city, serves_alcohol)
    return proc.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_tax_registration(legal_form: str) -> str:
    """Get the tax registration (Steuerliche Erfassung via ELSTER) step.

    Args:
        legal_form: One of "sole proprietor", "UG", or "GmbH"
    """
    step = elster.get_tax_registration_step(legal_form)
    return step.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_dguv_registration() -> str:
    """Get the accident insurance registration (DGUV / BGN) step."""
    step = dguv.get_dguv_registration_step()
    return step.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_social_insurance_registration() -> str:
    """Get the social insurance registration (Sozialversicherungsanmeldung) step.
    Required when the employer hires staff (Angestellte or Minijobber).
    This is an employer duty separate from the food-law IfSG instruction.
    """
    step = sozialversicherung.get_social_insurance_registration_step()
    return step.model_dump_json(indent=2)


@chat_agent.tool_plain
def get_location_risk(premises_type: str, has_public_terrace: bool = False) -> str:
    """Get location/zoning risk flags for a premises.

    Args:
        premises_type: One of "new_non_gastro", "existing_gastronomy", "change_of_use", "takeover"
        has_public_terrace: Whether outdoor seating on public land is planned
    """
    import json

    risks = geoportal.flag_location_risk(premises_type, has_public_terrace)
    return json.dumps([r.model_dump() for r in risks], indent=2, ensure_ascii=False)
