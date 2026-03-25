from __future__ import annotations

from app.schemas import ActionStep

CHECKED = "2026-03-25"


def get_social_insurance_registration_step() -> ActionStep:
    return ActionStep(
        title="Sozialversicherung: Mitarbeiter anmelden",
        description=(
            "Als Arbeitgeber müssen Sie jeden Mitarbeiter vor dem ersten Arbeitstag "
            "bei der zuständigen gesetzlichen Krankenkasse (GKV) zur Sozialversicherung "
            "anmelden (DEÜV-Meldung). Für geringfügig Beschäftigte (Minijobber) erfolgt "
            "die Anmeldung über die Minijob-Zentrale. Benötigt werden: Betriebsnummer (BBNR) "
            "vom Betriebsnummern-Service der Bundesagentur für Arbeit sowie die "
            "Sozialversicherungsnummer des Mitarbeiters."
        ),
        action_url="https://www.minijob-zentrale.de/DE/arbeitgeber/1_was_ist_ein_minijob/node.html",
        action_type="registration",
        source_url="https://www.bundesregierung.de/breg-de/themen/arbeit-und-soziales/sozialversicherung",
        last_checked_at=CHECKED,
    )
