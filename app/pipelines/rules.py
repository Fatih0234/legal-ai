from __future__ import annotations

from app.schemas import CaseFlags, CaseProfile, LegalForm, PremisesType


def derive_flags(case: CaseProfile) -> CaseFlags:
    """Derive required procedure flags from a case profile.

    Rules:
    - always: trade registration
    - always: food business registration
    - ifsg: if employees_handle_food OR founder_handles_food
    - restaurant_permit: if serves_alcohol AND has_seating (on-premises consumption)
    - ihk_instruction: same as restaurant_permit (Unterrichtung im Gaststättenrecht)
    - commercial_register: if legal_form is UG or GmbH
    - location_followup: if premises_type != existing_gastronomy
    - change_of_use_permit: if premises_type == change_of_use
    - public_terrace_permit: if has_public_terrace
    - takeover_verification: if premises_type == takeover
    - social_insurance: if has_employees
    """
    needs_restaurant_permit = case.serves_alcohol and case.has_seating
    return CaseFlags(
        needs_trade_registration=True,
        needs_food_registration=True,
        needs_ifsg=case.employees_handle_food or case.founder_handles_food,
        needs_restaurant_permit=needs_restaurant_permit,
        needs_ihk_instruction=needs_restaurant_permit,
        needs_commercial_register=case.legal_form in (LegalForm.UG, LegalForm.GMBH),
        needs_location_followup=case.premises_type != PremisesType.EXISTING_GASTRONOMY,
        needs_change_of_use_permit=case.premises_type == PremisesType.CHANGE_OF_USE,
        needs_public_terrace_permit=case.has_public_terrace,
        needs_takeover_verification=case.premises_type == PremisesType.TAKEOVER,
        needs_social_insurance=case.has_employees,
    )
