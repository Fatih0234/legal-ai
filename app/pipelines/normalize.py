from __future__ import annotations

import re
from datetime import UTC, datetime

from bs4 import BeautifulSoup, Tag

from app.schemas import Procedure


def _get_panel(soup: BeautifulSoup, *section_ids: str):
    """Find an accordion panel by one of the given section IDs."""
    for sid in section_ids:
        panel = soup.find(id=f"{sid}-panel")
        if panel is not None:
            return panel
    return None


def _get_text(soup: BeautifulSoup, *section_ids: str) -> str:
    """Extract plain text from an accordion section (try DE then EN IDs)."""
    panel = _get_panel(soup, *section_ids)
    if panel is None:
        return ""
    for tag in panel.find_all(["script", "style", "i"]):
        tag.decompose()
    return panel.get_text(separator="\n", strip=True)


def _get_top_level_items(soup: BeautifulSoup, *section_ids: str) -> list[str]:
    """Extract top-level <li> items (no nested children) as strings."""
    panel = _get_panel(soup, *section_ids)
    if panel is None:
        return []
    items: list[str] = []
    for li in panel.find_all("li"):
        if li.find_parent("li") is not None:
            continue
        text = li.get_text(separator=" ", strip=True)
        if len(text) > 5:
            items.append(text)
    return items


def _extract_region(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"name": "region"})
    if meta and isinstance(meta, Tag):
        return str(meta.get("content", ""))
    return ""


def _extract_publisher(soup: BeautifulSoup) -> str:
    aside = soup.find(class_="lv-aside-new__imprint-editor")
    if aside:
        return aside.get_text(strip=True)
    return ""


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_sdg_page(html: str, source_url: str = "") -> Procedure:
    """Parse an SDG page HTML into a Procedure object.

    Tries German section IDs first, falls back to English.
    - beschreibung / description: informational text
    - verfahrensablauf / procedure: actual steps
    - unterlagen / documents: required documents
    - voraussetzungen / preconditions: preconditions
    - kosten / costs: fees
    - handlungsgrundlagen / legal: legal basis
    """
    soup = BeautifulSoup(html, "lxml")

    # Title
    title_tag = soup.find("muse-text", class_="lv-leistung__heading")
    title = title_tag.get_text(strip=True) if title_tag else ""
    if not title:
        title_tag = soup.find("lv-card-ce", class_="lv-leistung__intro-text")
        title = str(title_tag.get("heading", "")) if title_tag else ""

    # Description
    intro = soup.find("lv-card-ce", class_="lv-leistung__intro-text")
    intro_desc = ""
    if intro and isinstance(intro, Tag):
        intro_desc = intro.get_text(strip=True)

    desc_text = _get_text(soup, "beschreibung", "description")
    description = desc_text if desc_text else intro_desc

    # Steps: prefer procedure panel
    steps = _get_top_level_items(soup, "verfahrensablauf", "procedure")
    if not steps:
        proc_text = _get_text(soup, "verfahrensablauf", "procedure")
        if proc_text:
            lines = [l.strip() for l in proc_text.split("\n") if l.strip()]
            steps = [l for l in lines if len(l) > 20]

    if not steps:
        steps = _get_top_level_items(soup, "beschreibung", "description")

    # Documents
    documents = _get_top_level_items(soup, "unterlagen", "documents")

    # Preconditions
    preconditions = _get_top_level_items(soup, "voraussetzungen", "preconditions")

    # Costs
    costs_text = _get_text(soup, "kosten", "costs")

    # Legal basis
    legal_text = _get_text(soup, "handlungsgrundlagen", "legal")

    # Publisher
    publisher = _extract_publisher(soup)

    # Build enriched description
    full_description = description
    if preconditions:
        full_description += "\n\nVoraussetzungen:\n" + "\n".join(
            f"- {p}" for p in preconditions
        )
    if documents:
        full_description += "\n\nErforderliche Unterlagen:\n" + "\n".join(
            f"- {d}" for d in documents
        )
    if costs_text:
        full_description += f"\n\nGebühren: {_clean_text(costs_text)}"
    if legal_text:
        full_description += f"\n\nRechtsgrundlage: {_clean_text(legal_text)}"

    return Procedure(
        title=title or "Unknown Procedure",
        description=full_description.strip(),
        steps=steps,
        source_url=source_url,
        source_name=f"SDG Portal ({publisher})" if publisher else "SDG Portal",
        last_checked_at=datetime.now(tz=UTC).strftime("%Y-%m-%d"),
        state_specific=True,
        category="",
    )
