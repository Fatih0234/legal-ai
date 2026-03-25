from __future__ import annotations

from app.schemas import CaseFlags, CaseProfile, LegalForm


def derive_flags(case: CaseProfile) -> CaseFlags:
    """Derive required procedure flags from a case profile.

    Rules:
    - always: trade registration
    - always: food business registration
    - ifsg: if employees_handle_food OR founder_handles_food
    - restaurant_permit: if serves_alcohol AND has_seating (on-premises consumption)
    - ihk_instruction: same as restaurant_permit (Unterrichtung im Gaststättenrecht)
    - commercial_register: if legal_form is UG or GmbH
    - location_followup: if not existing_gastro_premises
    """
    needs_restaurant_permit = case.serves_alcohol and case.has_seating
    return CaseFlags(
        needs_trade_registration=True,
        needs_food_registration=True,
        needs_ifsg=case.employees_handle_food or case.founder_handles_food,
        needs_restaurant_permit=needs_restaurant_permit,
        needs_ihk_instruction=needs_restaurant_permit,
        needs_commercial_register=case.legal_form in (LegalForm.UG, LegalForm.GMBH),
        needs_location_followup=not case.existing_gastro_premises,
    )
