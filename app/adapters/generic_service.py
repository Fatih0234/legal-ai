from __future__ import annotations

from app.schemas import Procedure

CHECKED = "2026-03-25"


def get_restaurant_permit(state: str, city: str, serves_alcohol: bool) -> Procedure:
    """Generic fallback for states without a dedicated static adapter."""
    if not serves_alcohol:
        return Procedure(
            title=f"Gastronomie — kein Alkoholausschank ({state})",
            description=(
                f"Ohne Alkoholausschank ist in {state} in der Regel keine "
                "Gaststättenerlaubnis erforderlich. Bitte beim Ordnungsamt Ihrer "
                "Stadt bestätigen lassen."
            ),
            steps=[
                "Beim Ordnungsamt bestätigen lassen, dass keine Erlaubnis nötig ist",
                "Mit den regulären Anmeldungen fortfahren",
            ],
            source_url="https://www.gesetze-im-internet.de/gastg/",
            source_name="Gaststättengesetz (Bund)",
            last_checked_at=CHECKED,
            state_specific=True,
            category="permit",
        )

    return Procedure(
        title=f"Gaststättenerlaubnis ({state})",
        description=(
            f"Wer in {state} alkoholische Getränke ausschenkt, benötigt eine "
            "Gaststättenerlaubnis oder eine entsprechende Erlaubnis nach Landesrecht. "
            "Zuständig ist das Ordnungsamt Ihrer Stadt/Gemeinde."
        ),
        steps=[
            "Unterlagen zusammenstellen: Führungszeugnis, Gewerbezentralauszug, "
            "Nachweis der persönlichen Zuverlässigkeit",
            "Gegebenenfalls Nachweis der Belehrung nach IfSG §43 vorlegen",
            "Antrag beim Ordnungsamt einreichen",
            "Gebühr bezahlen (variiert je nach Gemeinde, typisch 100–400 EUR)",
            "Auf Bearbeitung warten (typisch 4–12 Wochen)",
        ],
        source_url="https://www.gesetze-im-internet.de/gastg/",
        source_name="Gaststättengesetz (Bund)",
        last_checked_at=CHECKED,
        state_specific=True,
        category="permit",
    )
