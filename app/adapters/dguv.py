from __future__ import annotations

from app.schemas import ActionStep

CHECKED = "2026-03-24"


def get_dguv_registration_step() -> ActionStep:
    return ActionStep(
        title="DGUV Unfallversicherung anmelden",
        description=(
            "Als Arbeitgeber müssen Sie sich bei der Berufsgenossenschaft "
            "für die gesetzliche Unfallversicherung (DGUV) anmelden. "
            "Für den Lebensmittel-/Gastronomiebereich ist dies in der Regel die BGN "
            "(Berufsgenossenschaft Nahrungsmittel und Gastgewerbe)."
        ),
        action_url="https://www.bgn.de/unternehmen/anmelden",
        action_type="insurance",
        source_url="https://www.dguv.de",
        last_checked_at=CHECKED,
    )
