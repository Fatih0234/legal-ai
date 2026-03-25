"""Run all 5 scenarios through the pipeline and log structured output."""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.orchestrator import evaluate_case, gather_procedures, build_checklist
from app.pipelines.rules import derive_flags
from app.schemas import CaseProfile

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> CaseProfile:
    return CaseProfile.model_validate(json.loads((FIXTURES / name).read_text()))


SCENARIOS = [
    (
        "01",
        "Berlin minimal (no alcohol, existing premises, no employees)",
        "scenario_01_berlin_minimal.json",
    ),
    (
        "02",
        "Berlin full (alcohol, new premises, employees, UG)",
        "scenario_02_berlin_full.json",
    ),
    (
        "03",
        "NRW minimal (no alcohol, takeaway, existing premises)",
        "scenario_03_nrw_minimal.json",
    ),
    (
        "04",
        "NRW full (alcohol, new premises, employees, GmbH)",
        "scenario_04_nrw_full.json",
    ),
    (
        "05",
        "NRW middle (no alcohol, seating, new premises, employees)",
        "scenario_05_nrw_middle.json",
    ),
]


async def run_scenario(num: str, desc: str, fixture: str):
    print(f"\n{'=' * 80}")
    print(f"SCENARIO {num}: {desc}")
    print(f"{'=' * 80}")

    case = _load(fixture)
    print(f"\n--- INPUT ---")
    print(json.dumps(case.model_dump(), indent=2))

    # Step 1: Rules
    flags = derive_flags(case)
    print(f"\n--- FLAGS ---")
    print(json.dumps(flags.model_dump(), indent=2))

    # Step 2: Procedures (static mode)
    procedures, action_steps, risk_flags = gather_procedures(case)
    print(f"\n--- PROCEDURES ({len(procedures)}) ---")
    for p in procedures:
        print(f"  [{p.category}] {p.title}")
        print(f"    Steps: {len(p.steps)} | Source: {p.source_url[:60]}...")

    print(f"\n--- ACTION STEPS ({len(action_steps)}) ---")
    for a in action_steps:
        print(f"  [{a.action_type}] {a.title}")

    print(f"\n--- RISK FLAGS ({len(risk_flags)}) ---")
    for r in risk_flags:
        print(f"  [{r.severity}] {r.category}: {r.description[:80]}")

    # Step 3: Checklist (no agent)
    result = build_checklist(case, procedures, action_steps)
    print(f"\n--- CHECKLIST ---")
    print(f"  Must do: {len(result.must_do_now)} items")
    for item in result.must_do_now:
        print(f"    - {item}")
    print(f"  Conditional: {len(result.conditional_steps)} items")
    for item in result.conditional_steps:
        print(f"    - {item}")
    print(f"  Documents: {result.documents}")
    print(f"  Authorities: {result.authorities}")
    print(f"  Links: {len(result.official_links)}")

    print(f"\n--- FULL JSON (without agent) ---")
    output = result.model_dump()
    output.pop("summary", None)
    output.pop("open_questions", None)
    print(json.dumps(output, indent=2, default=str))


async def main():
    for num, desc, fixture in SCENARIOS:
        await run_scenario(num, desc, fixture)


if __name__ == "__main__":
    asyncio.run(main())
