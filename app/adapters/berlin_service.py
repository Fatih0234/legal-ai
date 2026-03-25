from __future__ import annotations

from app.schemas import Procedure

CHECKED = "2026-03-24"


def get_restaurant_permit(state: str, city: str, serves_alcohol: bool) -> Procedure:
    if not serves_alcohol:
        return Procedure(
            title="Gastronomie — kein Alkoholausschank",
            description=(
                "Ohne Alkoholausschank ist in Berlin keine Gaststättenerlaubnis erforderlich. "
                "Die reguläre Gewerbeanmeldung und Lebensmittelregistrierung genügen."
            ),
            steps=[
                "Beim Ordnungsamt bestätigen lassen, dass für Ihr Konzept keine Erlaubnis nötig ist",
                "Mit den regulären Anmeldungen fortfahren",
            ],
            source_url="https://service.berlin.de/dienstleistung/326520/",
            source_name="Service Berlin",
            last_checked_at=CHECKED,
            state_specific=True,
            category="permit",
        )

    return Procedure(
        title="Gaststättenerlaubnis — Berlin",
        description=(
            "Wer in Berlin alkoholische Getränke ausschenkt, benötigt eine "
            "Gaststättenerlaubnis vom Ordnungsamt."
        ),
        steps=[
            "Erforderliche Unterlagen zusammenstellen: Führungszeugnis, "
            "Gewerbezentralauszug, Nachweis der IHK-Unterrichtung",
            "Antragsformular für die Gaststättenerlaubnis ausfüllen",
            "Beim zuständigen Ordnungsamt einreichen",
            "Gebühr bezahlen (ca. 50–200 EUR in Berlin)",
            "Auf Bearbeitung warten (in der Regel 4–8 Wochen)",
            "Gegebenenfalls an Klärungsgesprächen teilnehmen",
        ],
        source_url="https://service.berlin.de/dienstleistung/326520/",
        source_name="Service Berlin",
        last_checked_at=CHECKED,
        state_specific=True,
        category="permit",
    )


def get_ihk_instruction(state: str, city: str, serves_alcohol: bool) -> Procedure:
    if not serves_alcohol:
        return Procedure(
            title="IHK Unterrichtung — nicht erforderlich",
            description="Die IHK-Unterrichtung ist nur bei Alkoholausschank erforderlich.",
            steps=[],
            source_url="",
            source_name="",
            last_checked_at=CHECKED,
            state_specific=True,
            category="instruction",
        )

    return Procedure(
        title="IHK Unterrichtung — Berlin",
        description=(
            "Vor dem Antrag auf eine Gaststättenerlaubnis muss der Antragsteller "
            "eine Gastronomie-Unterrichtung bei der zuständigen IHK absolvieren."
        ),
        steps=[
            "Für die IHK-Unterrichtung (Gastronomie-Schulung) anmelden",
            "Unterrichtung besuchen — umfasst Hygiene, Lebensmittelrecht, Alkoholregulierung",
            "IHK-Zertifikat erhalten",
            "Zertifikat zusammen mit dem Gaststättenerlaubnis-Antrag einreichen",
        ],
        source_url="https://www.ihk.de/berlin/branchen/gastronomie-und-tourismus-2606856",
        source_name="IHK Berlin",
        last_checked_at=CHECKED,
        state_specific=True,
        category="instruction",
    )
