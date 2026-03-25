from __future__ import annotations

from app.schemas import Procedure

CHECKED = "2026-03-24"


def get_business_registration(state: str, city: str) -> Procedure:
    return Procedure(
        title="Gewerbeanmeldung NRW",
        description=(
            "Melden Sie Ihr Gewerbe beim zuständigen Gewerbeamt in NRW an. "
            "Das Verfahren erfolgt auf kommunaler Ebene."
        ),
        steps=[
            "Zuständiges Gewerbeamt für Ihre Stadt/Gemeinde ermitteln",
            "Personalausweis, Mietvertrag und ggf. erforderliche Genehmigungen bereithalten",
            "Formular für die Gewerbeanmeldung ausfüllen",
            "Beim Rathaus oder Bürgerbüro einreichen",
            "Gebühr bezahlen (variiert nach Gemeinde, in der Regel 20–60 EUR)",
            "Gewerbeschein entgegennehmen",
        ],
        source_url="https://www.wirtschaft.nrw/gewerbeanmeldung",
        source_name="Wirtschaft.NRW",
        last_checked_at=CHECKED,
        state_specific=True,
        category="trade",
    )


def get_restaurant_permit(state: str, city: str, serves_alcohol: bool) -> Procedure:
    if not serves_alcohol:
        return Procedure(
            title="Gastronomie — kein Alkoholausschank",
            description=(
                "Ohne Alkoholausschank ist in NRW keine Gaststättenerlaubnis erforderlich. "
                "Die regulären Anmeldungen gelten."
            ),
            steps=[
                "Beim Ordnungsamt bestätigen lassen, dass keine Erlaubnis nötig ist",
                "Mit den regulären Anmeldungen fortfahren",
            ],
            source_url="https://www.wirtschaft.nrw/gastronomie",
            source_name="Wirtschaft.NRW",
            last_checked_at=CHECKED,
            state_specific=True,
            category="permit",
        )

    return Procedure(
        title="Gaststättenerlaubnis NRW",
        description=(
            "Wer in NRW alkoholische Getränke ausschenkt, benötigt eine "
            "Gaststättenerlaubnis vom Ordnungsamt der Gemeinde."
        ),
        steps=[
            "Unterlagen zusammenstellen: Führungszeugnis, Gewerbezentralauszug, "
            "Nachweis der persönlichen Zuverlässigkeit",
            "Gegebenenfalls Nachweis der Belehrung nach IfSG §43 vorlegen",
            "Antrag auf Gaststättenerlaubnis ausfüllen",
            "Beim Ordnungsamt einreichen",
            "Gebühr bezahlen (variiert nach Gemeinde)",
            "Auf Bearbeitung warten (in der Regel 4–12 Wochen)",
        ],
        source_url="https://www.wirtschaft.nrw/gastronomie",
        source_name="Wirtschaft.NRW",
        last_checked_at=CHECKED,
        state_specific=True,
        category="permit",
    )
