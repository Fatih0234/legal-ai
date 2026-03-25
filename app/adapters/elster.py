from __future__ import annotations

from app.schemas import ActionStep, LegalForm

CHECKED = "2026-03-24"


def get_tax_registration_step(legal_form: str) -> ActionStep:
    if legal_form in (LegalForm.UG, LegalForm.GMBH):
        return ActionStep(
            title="Steuerliche Erfassung über ELSTER — GmbH/UG",
            description=(
                "Als GmbH oder UG müssen Sie die steuerliche Erfassung über ELSTER "
                "durchführen. Dies umfasst Körperschaftsteuer, Gewerbesteuer, Umsatzsteuer "
                "und ggf. Lohnsteuer bei Beschäftigten."
            ),
            action_url="https://www.elster.de/eportal/formulare-leistungen/alleformulare",
            action_type="registration",
            source_url="https://www.elster.de",
            last_checked_at=CHECKED,
        )

    return ActionStep(
        title="Steuerliche Erfassung über ELSTER — Einzelunternehmer",
        description=(
            "Registrieren Sie sich steuerlich über ELSTER. Sie benötigen Ihre "
            "Gewerbeanmeldedaten. Das Finanzamt vergibt Ihre Steuernummer. "
            "Die Umsatzsteuer-Registrierung gilt, wenn der Umsatz die "
            "Kleinunternehmergrenze überschreitet oder Sie auf die Regelbesteuerung optieren."
        ),
        action_url="https://www.elster.de/eportal/formulare-leistungen/alleformulare",
        action_type="registration",
        source_url="https://www.elster.de",
        last_checked_at=CHECKED,
    )
