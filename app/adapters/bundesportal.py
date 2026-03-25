from __future__ import annotations

from app.schemas import Procedure

CHECKED = "2026-03-24"


def get_trade_registration(state: str, city: str) -> Procedure:
    return Procedure(
        title="Gewerbeanmeldung",
        description=(
            "Melden Sie Ihr Gewerbe beim zuständigen Gewerbeamt an. "
            "Dies ist für alle gewerblichen Lebensmittelbetriebe Pflicht."
        ),
        steps=[
            "Personalausweis/Reisepass und Mietvertrag für die Geschäftsräume bereithalten",
            "Formular für die Gewerbeanmeldung ausfüllen",
            "Beim zuständigen Gewerbeamt einreichen",
            "Gebühr bezahlen (in der Regel 20–60 EUR)",
            "Gewerbeschein entgegennehmen",
        ],
        source_url="https://verwaltung.bund.de/leistungsverzeichnis/en/leistung/99057001060000",
        source_name="SDG Portal",
        last_checked_at=CHECKED,
        state_specific=False,
        category="trade",
    )


def get_food_business_registration(state: str, city: str) -> Procedure:
    return Procedure(
        title="Lebensmittelbetrieb registrieren lassen",
        description=(
            "Registrieren Sie Ihren Lebensmittelbetrieb beim zuständigen "
            "Veterinär- und Lebensmittelaufsichtsamt."
        ),
        steps=[
            "Zuständiges Veterinär- und Lebensmittelaufsichtsamt für Ihren Bezirk ermitteln",
            "Formular zur Registrierung des Lebensmittelbetriebs ausfüllen",
            "Vor Betriebsaufnahme einreichen",
            "Mit einer Erstkontrolle durch Lebensmittelaufsichtsbeamte rechnen",
        ],
        source_url="https://verwaltung.bund.de/leistungsverzeichnis/en/leistung/99050048060000",
        source_name="SDG Portal",
        last_checked_at=CHECKED,
        state_specific=False,
        category="food",
    )


def get_ifsg_instruction(state: str, city: str) -> Procedure:
    return Procedure(
        title="Belehrung nach IfSG (Infektionsschutzgesetz)",
        description=(
            "Alle Mitarbeiter, die offene Lebensmittel bearbeiten, müssen vor "
            "Arbeitsaufnahme eine Erstbelehrung nach §43 IfSG absolvieren, "
            "danach alle 2 Jahre eine Folgebelehrung."
        ),
        steps=[
            "Termin beim zuständigen Gesundheitsamt vereinbaren",
            "Erstbelehrung besuchen — Personalausweis mitbringen",
            "Belehrungsbescheinigung erhalten",
            "Bescheinigung im Betrieb aufbewahren",
            "Folgebelehrung alle 24 Monate einplanen",
        ],
        source_url="https://verwaltung.bund.de/leistungsverzeichnis/en/leistung/99003002022000",
        source_name="SDG Portal",
        last_checked_at=CHECKED,
        state_specific=False,
        category="health",
    )
