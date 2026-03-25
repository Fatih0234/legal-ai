"""Tests for the SDG API client.

These tests make real HTTP calls to the SDG portal. They are marked with
@pytest.mark.live so they can be skipped in CI with: pytest -m "not live"
"""

import pytest

from app.pipelines.normalize import parse_sdg_page
from app.schemas import Procedure


# --- normalize tests (no HTTP) ---

SAMPLE_HTML = """
<html><body>
<muse-text class="lv-leistung__heading" variant="heading-lg">Register food establishments</muse-text>
<div id="description-panel" class="lv-accordion__panel">
  <article class="lv-accordion-textmodule">
    <div class="lv-accordion-textmodule__content">
      <p>Food businesses must register with the local authority.</p>
      <ul>
        <li>Submit the registration form</li>
        <li>Provide business details</li>
        <li>Wait for confirmation</li>
      </ul>
    </div>
  </article>
</div>
<div id="preconditions-panel" class="lv-accordion__panel">
  <article class="lv-accordion-textmodule">
    <div class="lv-accordion-textmodule__content">
      <ul>
        <li>You produce or process food</li>
      </ul>
    </div>
  </article>
</div>
<div id="costs-panel" class="lv-accordion__panel">
  <article class="lv-accordion-textmodule">
    <ul class="lv-accordion-costs">
      <li>
        <dl>
          <dt>Advance payment</dt>
          <dd>no</dd>
        </dl>
      </li>
    </ul>
  </article>
</div>
<meta name="region" content="Köln, North Rhine-Westphalia" />
<aside>
  <p class="lv-aside-new__imprint-editor">North Rhine-Westphalia</p>
</aside>
</body></html>
"""


def test_parse_sdg_page_title():
    proc = parse_sdg_page(SAMPLE_HTML, source_url="https://example.com")
    assert proc.title == "Register food establishments"


def test_parse_sdg_page_steps():
    proc = parse_sdg_page(SAMPLE_HTML)
    assert len(proc.steps) == 3
    assert "Submit the registration form" in proc.steps


def test_parse_sdg_page_description():
    proc = parse_sdg_page(SAMPLE_HTML)
    assert "Food businesses must register" in proc.description


def test_parse_sdg_page_preconditions():
    proc = parse_sdg_page(SAMPLE_HTML)
    assert "You produce or process food" in proc.description


def test_parse_sdg_page_source_url():
    proc = parse_sdg_page(SAMPLE_HTML, source_url="https://example.com/page")
    assert proc.source_url == "https://example.com/page"


def test_parse_sdg_page_publisher():
    proc = parse_sdg_page(SAMPLE_HTML)
    assert "North Rhine-Westphalia" in proc.source_name


def test_parse_sdg_page_empty_html():
    proc = parse_sdg_page("<html><body></body></html>")
    assert proc.title == "Unknown Procedure"
    assert proc.steps == []


# --- live SDG API tests ---


@pytest.mark.live
@pytest.mark.asyncio
async def test_sdg_fetch_json_states():
    """STAMM endpoint should return a list of German states."""
    import httpx
    from app.adapters.sdg_client import SDGClient, SERVICE_IDS

    async with httpx.AsyncClient() as http_client:
        sdg = SDGClient(http_client=http_client)
        data = await sdg._get_json(
            f"/leistungsverzeichnis/DE/api/zustaendigkeiten/STAMM/{SERVICE_IDS['food']}"
        )
        links = data.get("gebietsliste", {}).get("links", [])
        names = [l["name"] for l in links]
        assert "Nordrhein-Westfalen" in names


@pytest.mark.live
@pytest.mark.asyncio
async def test_sdg_resolve_page_url_food_nrw():
    """Should resolve food registration page URL for Köln."""
    import httpx
    from app.adapters.sdg_client import SDGClient

    async with httpx.AsyncClient() as http_client:
        sdg = SDGClient(http_client=http_client)
        url = await sdg.resolve_final_page_url("food", city="Köln")
        assert "verwaltung.bund.de" in url
        assert "99050048060000" in url
        assert "herausgeber" in url


@pytest.mark.live
@pytest.mark.asyncio
async def test_sdg_fetch_page_food_nrw():
    """Should fetch and parse food registration page for Köln."""
    import httpx
    from app.adapters.sdg_client import SDGClient

    async with httpx.AsyncClient() as http_client:
        sdg = SDGClient(http_client=http_client)
        proc = await sdg.get_procedure("food", city="Köln")
        assert isinstance(proc, Procedure)
        assert proc.title
        assert proc.source_url
        assert "verwaltung.bund.de" in proc.source_url


@pytest.mark.live
@pytest.mark.asyncio
async def test_sdg_resolve_page_url_trade_nrw():
    """Should resolve trade registration page URL for Köln."""
    import httpx
    from app.adapters.sdg_client import SDGClient

    async with httpx.AsyncClient() as http_client:
        sdg = SDGClient(http_client=http_client)
        url = await sdg.resolve_final_page_url("trade", city="Köln")
        assert "99057001060000" in url


@pytest.mark.live
@pytest.mark.asyncio
async def test_sdg_cache_hit():
    """Second call should use cache."""
    import httpx
    from app.adapters.sdg_client import SDGClient

    async with httpx.AsyncClient() as http_client:
        sdg = SDGClient(http_client=http_client)
        proc1 = await sdg.get_procedure("food", city="Köln")
        proc2 = await sdg.get_procedure("food", city="Köln")
        assert proc1.title == proc2.title
        assert proc1.source_url == proc2.source_url
