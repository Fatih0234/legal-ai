from __future__ import annotations

from app.schemas import CaseFlags, CaseProfile


def derive_flags(case: CaseProfile) -> CaseFlags:
    """Derive required procedure flags from a case profile.

    Rules (from PRD):
    - always: trade registration
    - always: food business registration
    - ifsg: if employees_handle_food
    - restaurant_permit: if serves_alcohol
    - location_followup: if not existing_gastro_premises
    """
    return CaseFlags(
        needs_trade_registration=True,
        needs_food_registration=True,
        needs_ifsg=case.employees_handle_food,
        needs_restaurant_permit=case.serves_alcohol,
        needs_location_followup=not case.existing_gastro_premises,
    )
