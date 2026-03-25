from app.pipelines.rules import derive_flags
from app.schemas import CaseProfile, LegalForm, State


def test_berlin_no_alcohol_flags():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        serves_alcohol=False,
        employees_handle_food=True,
        founder_handles_food=False,
        existing_gastro_premises=False,
    )
    flags = derive_flags(case)
    assert flags.needs_trade_registration is True
    assert flags.needs_food_registration is True
    assert flags.needs_ifsg is True
    assert flags.needs_restaurant_permit is False
    assert flags.needs_ihk_instruction is False
    assert flags.needs_location_followup is True


def test_berlin_alcohol_flags():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        serves_alcohol=True,
        has_seating=True,
        employees_handle_food=True,
        founder_handles_food=False,
        existing_gastro_premises=False,
        legal_form=LegalForm.UG,
    )
    flags = derive_flags(case)
    assert flags.needs_trade_registration is True
    assert flags.needs_food_registration is True
    assert flags.needs_ifsg is True
    assert flags.needs_restaurant_permit is True
    assert flags.needs_ihk_instruction is True
    assert flags.needs_location_followup is True


def test_nrw_takeaway_no_employees():
    case = CaseProfile(
        state=State.NRW,
        city="Köln",
        serves_alcohol=False,
        employees_handle_food=False,
        founder_handles_food=False,
        existing_gastro_premises=True,
    )
    flags = derive_flags(case)
    assert flags.needs_trade_registration is True
    assert flags.needs_food_registration is True
    assert flags.needs_ifsg is False
    assert flags.needs_restaurant_permit is False
    assert flags.needs_ihk_instruction is False
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
        founder_handles_food=False,
    )
    flags = derive_flags(case)
    assert flags.needs_ifsg is False


# --- New tests ---

def test_alcohol_no_seating_no_permit():
    """Alcohol + no seating (takeaway) → no permit, no IHK."""
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        serves_alcohol=True,
        has_seating=False,
        takeaway_only=True,
    )
    flags = derive_flags(case)
    assert flags.needs_restaurant_permit is False
    assert flags.needs_ihk_instruction is False


def test_alcohol_seating_permit_and_ihk():
    """Alcohol + seating → permit + IHK."""
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        serves_alcohol=True,
        has_seating=True,
    )
    flags = derive_flags(case)
    assert flags.needs_restaurant_permit is True
    assert flags.needs_ihk_instruction is True


def test_founder_handles_food_only_ifsg():
    """Founder handles food (no employees) → IfSG required."""
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        employees_handle_food=False,
        founder_handles_food=True,
    )
    flags = derive_flags(case)
    assert flags.needs_ifsg is True


def test_neither_handles_food_no_ifsg():
    """Neither founder nor employees handle food → no IfSG."""
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        employees_handle_food=False,
        founder_handles_food=False,
    )
    flags = derive_flags(case)
    assert flags.needs_ifsg is False


def test_ug_needs_commercial_register():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        legal_form=LegalForm.UG,
    )
    flags = derive_flags(case)
    assert flags.needs_commercial_register is True


def test_gmbh_needs_commercial_register():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        legal_form=LegalForm.GMBH,
    )
    flags = derive_flags(case)
    assert flags.needs_commercial_register is True


def test_sole_proprietor_no_commercial_register():
    case = CaseProfile(
        state=State.BERLIN,
        city="Berlin",
        legal_form=LegalForm.SOLE_PROPRIETOR,
    )
    flags = derive_flags(case)
    assert flags.needs_commercial_register is False
