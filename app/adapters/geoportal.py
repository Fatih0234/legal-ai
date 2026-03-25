from __future__ import annotations

from app.schemas import RiskFlag

CHECKED = "2026-03-24"


def find_geo_sources(state: str, city: str) -> list[dict[str, str]]:
    """Return geo discovery sources for the given location."""
    sources = [
        {
            "name": "Geoportal Deutschland",
            "url": "https://www.geoportal.de",
            "description": "Bundesweites Geoportal für Geodaten",
        },
        {
            "name": "GDI-DE (Geodateninfrastruktur Deutschland)",
            "url": "https://www.gdi-de.org",
            "description": "Deutsche Geodateninfrastruktur",
        },
    ]
    if state == "Berlin":
        sources.append(
            {
                "name": "FIS-Broker Berlin",
                "url": "https://fbinter.stadt-berlin.de/fb/",
                "description": "Geodatensystem der Stadt Berlin",
            }
        )
    elif state == "NRW":
        sources.append(
            {
                "name": "GDI NRW",
                "url": "https://www.geoportal.nrw",
                "description": "Geodatenportal NRW",
            }
        )
    return sources


def flag_location_risk(existing_gastro_premises: bool) -> list[RiskFlag]:
    """Flag zoning / change-of-use risk for non-existing gastro premises."""
    if existing_gastro_premises:
        return [
            RiskFlag(
                category="Räumlichkeiten",
                description=(
                    "Bestehende Gastronomie-Räumlichkeiten — kein Nutzungsänderungsrisiko."
                ),
                severity="info",
                recommendation=(
                    "Bestätigen Sie, dass die bestehende Genehmigung "
                    "Ihre geplante Nutzung abdeckt."
                ),
                source_url="",
            )
        ]

    return [
        RiskFlag(
            category="Räumlichkeiten",
            description=(
                "Diese Location wurde bisher nicht als Gastronomie genutzt. "
                "Möglicherweise benötigen Sie eine Nutzungsänderungsgenehmigung "
                "von der Bauaufsichtsbehörde."
            ),
            severity="warning",
            recommendation=(
                "Kontaktieren Sie Ihr lokales Bauamt, bevor Sie einen Mietvertrag "
                "unterschreiben. Prüfen Sie, ob die Baugenehmigung die Gastronomienutzung "
                "(Nutzungsart) abdeckt. Falls nicht, müssen Sie einen Antrag auf "
                "Nutzungsänderung stellen."
            ),
            source_url="",
        ),
        RiskFlag(
            category="Bebauungsplan",
            description=(
                "Prüfen Sie, ob der geplante Standort in einem Gebiet liegt, "
                "in dem Gastronomie erlaubt ist. Einige Wohngebiete haben "
                "Einschränkungen für gewerbliche Lebensmittelbetriebe."
            ),
            severity="info",
            recommendation=(
                "Beantragen Sie eine Bauakte für das Grundstück, um die "
                "bestehenden Nutzungsgenehmigungen zu verstehen."
            ),
            source_url="https://www.geoportal.de",
        ),
    ]
