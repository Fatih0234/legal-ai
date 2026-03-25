"""E2E tests: rules → adapters → checklist assembly (no LLM calls).

Tests the deterministic part of the pipeline. The LLM summary generation
is excluded here to keep tests fast and stable.
"""

import json
from pathlib import Path

from app.orchestrator import gather_procedures, build_checklist
from app.pipelines.rules import derive_flags
from app.schemas import CaseProfile

FIXTURES = Path(__file__).parent / "fixtures"


def _load_case(name: str) -> CaseProfile:
    raw = json.loads((FIXTURES / name).read_text())
    return CaseProfile.model_validate(raw)


def test_berlin_no_alcohol():
    case = _load_case("case_berlin_no_alcohol.json")
    procedures, action_steps, risk_flags = gather_procedures(case)

    titles = [p.title for p in procedures]
    assert any("Gewerbeanmeldung" in t for t in titles)
    assert any("Lebensmittel" in t for t in titles)
    assert any("IfSG" in t for t in titles)
    # No restaurant permit application
    assert not any(
        "Gaststättenerlaubnis" in t and "Berlin" in t and p.steps
        for p in procedures
        for t in [p.title]
        if p.category == "permit" and p.steps
    )

    result = build_checklist(case, procedures, action_steps)
    assert result.flags.needs_trade_registration is True
    assert result.flags.needs_restaurant_permit is False
    assert result.flags.needs_ifsg is True

    # Must-do includes trade, food, IfSG, ELSTER, DGUV
    assert len(result.must_do_now) >= 4
    assert result.official_links  # has source URLs

    # Snapshot stability: same input -> same output (excluding agent parts)
    result2 = build_checklist(case, *gather_procedures(case)[:2])
    assert result.must_do_now == result2.must_do_now
    assert result.conditional_steps == result2.conditional_steps


def test_berlin_alcohol_new_premises():
    case = _load_case("case_berlin_alcohol_new_premises.json")
    flags = derive_flags(case)

    assert flags.needs_restaurant_permit is True
    assert flags.needs_ifsg is True
    assert flags.needs_location_followup is True

    procedures, action_steps, risk_flags = gather_procedures(case)
    titles = [p.title for p in procedures]

    # Should have Gaststättenerlaubnis and IHK
    assert any("Gaststättenerlaubnis" in t for t in titles)
    assert any("IHK" in t for t in titles)

    # Should have risk flags for new premises
    assert len(risk_flags) >= 1
    assert any(r.severity == "warning" for r in risk_flags)

    result = build_checklist(case, procedures, action_steps)
    assert len(result.conditional_steps) >= 1  # restaurant permit
    assert len(result.must_do_now) >= 3
    # Documents should include clearance and trade extract
    assert any("Führungszeugnis" in d for d in result.documents)


def test_nrw_takeaway():
    case = _load_case("case_nrw_takeaway.json")
    flags = derive_flags(case)

    assert flags.needs_ifsg is False  # no employees handle food
    assert flags.needs_restaurant_permit is False
    assert flags.needs_location_followup is False  # existing premises

    procedures, action_steps, risk_flags = gather_procedures(case)

    # Should use NRW-specific registration
    nrw_procs = [p for p in procedures if p.state_specific]
    assert len(nrw_procs) >= 1

    result = build_checklist(case, procedures, action_steps)
    assert result.flags.needs_ifsg is False
    assert result.flags.needs_restaurant_permit is False

    # Risk flags should be info-level (existing premises)
    assert all(r.severity == "info" for r in risk_flags)


def test_snapshot_stability():
    """Same input must produce identical rule-based output."""
    case = _load_case("case_berlin_no_alcohol.json")

    results = []
    for _ in range(3):
        procedures, action_steps, risk_flags = gather_procedures(case)
        result = build_checklist(case, procedures, action_steps)
        results.append(result)

    for i in range(1, len(results)):
        assert results[0].must_do_now == results[i].must_do_now
        assert results[0].conditional_steps == results[i].conditional_steps
        assert results[0].official_links == results[i].official_links
        assert [p.title for p in results[0].procedures] == [
            p.title for p in results[i].procedures
        ]
        assert [a.title for a in results[0].action_steps] == [
            a.title for a in results[i].action_steps
        ]
