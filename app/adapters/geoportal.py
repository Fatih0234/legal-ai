from __future__ import annotations

from app.schemas import PremisesType, RiskFlag

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


def flag_location_risk(
    premises_type: PremisesType | str,
    has_public_terrace: bool = False,
) -> list[RiskFlag]:
    """Flag zoning / premises risk based on the type of location situation."""
    flags: list[RiskFlag] = []

    if premises_type == PremisesType.EXISTING_GASTRONOMY:
        flags.append(
            RiskFlag(
                category="Räumlichkeiten",
                description=(
                    "Bestehende Gastronomie-Räumlichkeiten — kein Nutzungsänderungsrisiko."
                ),
                severity="info",
                recommendation=(
                    "Bestätigen Sie, dass die bestehende Baugenehmigung "
                    "Ihre konkrete geplante Nutzung (z.B. Café vs. Restaurant) abdeckt."
                ),
                source_url="",
            )
        )

    elif premises_type == PremisesType.CHANGE_OF_USE:
        flags.append(
            RiskFlag(
                category="Nutzungsänderung",
                description=(
                    "Die Umnutzung eines Nicht-Gastronomieobjekts (z.B. Laden, Büro) "
                    "in einen Gastronomiebetrieb erfordert eine Baugenehmigung für "
                    "Nutzungsänderung (§ 59 BauO Bln / § 63 BauO NRW)."
                ),
                severity="warning",
                recommendation=(
                    "Stellen Sie vor Mietvertragsunterzeichnung einen Antrag auf "
                    "Nutzungsänderung bei der Bauaufsichtsbehörde. "
                    "Ohne gültige Baugenehmigung kann der Betrieb untersagt werden. "
                    "Prüfen Sie auch den Bebauungsplan auf zulässige Nutzungsarten."
                ),
                source_url="",
            )
        )
        flags.append(
            RiskFlag(
                category="Bebauungsplan",
                description=(
                    "Prüfen Sie, ob der geplante Standort in einem Gebiet liegt, "
                    "in dem Gastronomie zulässig ist. In reinen Wohngebieten (WR) "
                    "ist Gastronomie in der Regel nicht erlaubt."
                ),
                severity="info",
                recommendation=(
                    "Beantragen Sie eine Bauakte für das Grundstück und prüfen Sie "
                    "den Bebauungsplan (B-Plan) beim Stadtplanungsamt."
                ),
                source_url="https://www.geoportal.de",
            )
        )

    elif premises_type == PremisesType.TAKEOVER:
        flags.append(
            RiskFlag(
                category="Übernahme Gaststätte",
                description=(
                    "Eine Gaststättenerlaubnis ist personengebunden und nicht übertragbar. "
                    "Der Vorpächter konnte seine Erlaubnis nicht an Sie weitergeben."
                ),
                severity="warning",
                recommendation=(
                    "Beantragen Sie eine eigene Gaststättenerlaubnis beim Ordnungsamt. "
                    "Prüfen Sie außerdem, ob die bestehende Baugenehmigung für das "
                    "Objekt noch gültig ist und Ihre geplante Betriebsart abdeckt."
                ),
                source_url="",
            )
        )

    else:  # new_non_gastro
        flags.append(
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
            )
        )
        flags.append(
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
            )
        )

    if has_public_terrace:
        flags.append(
            RiskFlag(
                category="Außenbereich / Terrasse",
                description=(
                    "Tische und Stühle auf öffentlichem Grund (Gehweg, Platz) erfordern "
                    "eine Sondernutzungserlaubnis des Bezirksamts "
                    "(Straßen- und Grünflächenamt)."
                ),
                severity="warning",
                recommendation=(
                    "Beantragen Sie die Sondernutzungserlaubnis vor Saisonbeginn. "
                    "Die Erlaubnis ist in der Regel saisonal befristet und kostenpflichtig. "
                    "Größe und Möblierung müssen vorab genehmigt werden."
                ),
                source_url="",
            )
        )

    return flags
