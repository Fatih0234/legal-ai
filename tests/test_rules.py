from app.pipelines.rules import derive_flags
from app.schemas import CaseProfile, LegalForm, State


def test_berlin_no_alcohol_flags():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        serves_alcohol=False,
        employees_handle_food=True,
        existing_gastro_premises=False,
    )
    flags = derive_flags(case)
    assert flags.needs_trade_registration is True
    assert flags.needs_food_registration is True
    assert flags.needs_ifsg is True
    assert flags.needs_restaurant_permit is False
    assert flags.needs_location_followup is True


def test_berlin_alcohol_flags():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        serves_alcohol=True,
        employees_handle_food=True,
        existing_gastro_premises=False,
        legal_form=LegalForm.UG,
    )
    flags = derive_flags(case)
    assert flags.needs_trade_registration is True
    assert flags.needs_food_registration is True
    assert flags.needs_ifsg is True
    assert flags.needs_restaurant_permit is True
    assert flags.needs_location_followup is True


def test_nrw_takeaway_no_employees():
    case = CaseProfile(
        state=State.NRW,
        city="Köln",
        serves_alcohol=False,
        employees_handle_food=False,
        existing_gastro_premises=True,
    )
    flags = derive_flags(case)
    assert flags.needs_trade_registration is True
    assert flags.needs_food_registration is True
    assert flags.needs_ifsg is False
    assert flags.needs_restaurant_permit is False
    assert flags.needs_location_followup is False


def test_existing_premises_no_location_risk():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        existing_gastro_premises=True,
    )
    flags = derive_flags(case)
    assert flags.needs_location_followup is False


def test_no_food_employees_no_ifsg():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        employees_handle_food=False,
    )
    flags = derive_flags(case)
    assert flags.needs_ifsg is False
