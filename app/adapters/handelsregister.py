from __future__ import annotations

from app.schemas import ActionStep, LegalForm

CHECKED = "2026-03-25"


def get_handelsregister_step(legal_form: str) -> ActionStep:
    if legal_form == LegalForm.GMBH:
        capital = "mindestens €25.000 (mind. €12.500 bei Gründung einzuzahlen)"
        entity = "GmbH"
        articles = "Gesellschaftsvertrag (GmbH-Satzung)"
    else:  # UG
        capital = "mindestens €1 (vollständig bei Gründung einzuzahlen)"
        entity = "UG (haftungsbeschränkt)"
        articles = "Gesellschaftsvertrag (UG-Musterprotokoll möglich)"

    return ActionStep(
        title=f"Handelsregistereintragung — {entity}",
        description=(
            f"Die {entity} entsteht rechtlich erst mit Eintragung ins Handelsregister. "
            f"Stammkapital: {capital}. "
            "Ablauf: Gesellschaftsvertrag notariell beurkunden lassen → Geschäftskonto eröffnen "
            "und Stammkapital einzahlen → Notar reicht Antrag beim Amtsgericht ein → "
            "auf Eintragung warten (i. d. R. 2–4 Wochen). "
            "Erst danach ist die Gewerbeanmeldung möglich."
        ),
        action_url="https://www.handelsregister.de",
        action_type="registration",
        source_url="https://www.justiz.de/onlinedienste/elektronisches_handels_und_genossenschaftsregister/index.php",
        last_checked_at=CHECKED,
    )
