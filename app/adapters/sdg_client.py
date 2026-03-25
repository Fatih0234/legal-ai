from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx

import app.cache.sqlite as cache
from app.adapters.regions import REGION_CODES, STATE_CODES
from app.pipelines.normalize import parse_sdg_page
from app.schemas import Procedure

logger = logging.getLogger(__name__)

BASE = "https://verwaltung.bund.de"

SERVICE_IDS = {
    "trade": "99057001060000",
    "food": "99050048060000",
    "ifsg": "99003002022000",
}

RATE_LIMIT_DELAY = 0.2  # 5 req/s


@dataclass
class SDGClient:
    http_client: httpx.AsyncClient
    base_url: str = BASE

    async def _get_json(self, path: str) -> dict:
        if path.startswith("/"):
            url = f"{self.base_url}{path}"
        elif path.startswith("http"):
            url = path
        else:
            url = f"{self.base_url}/{path}"
        await asyncio.sleep(RATE_LIMIT_DELAY)
        resp = await self.http_client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    async def _get_html(self, path: str) -> str:
        if path.startswith("/"):
            url = f"{self.base_url}{path}"
        elif path.startswith("http"):
            url = path
        else:
            url = f"{self.base_url}/{path}"
        await asyncio.sleep(RATE_LIMIT_DELAY)
        resp = await self.http_client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text

    async def resolve_final_page_url(
        self, service_key: str, city: str = "Köln", state: str = "NRW"
    ) -> str:
        """Walk the SDG hierarchy to find the final page URL for a service + city + state."""
        service_id = SERVICE_IDS[service_key]
        state_code = STATE_CODES.get(state, "NW")
        region_codes = REGION_CODES.get(state, {})
        region_code = region_codes.get(city)

        # Step 1: STAMM → list of states
        stamm = await self._get_json(
            f"/leistungsverzeichnis/DE/api/zustaendigkeiten/STAMM/{service_id}"
        )
        state_link = None
        for link in stamm.get("gebietsliste", {}).get("links", []):
            if f"/{state_code}/" in link.get("url", ""):
                state_link = link["url"]
                break
        if state_link is None:
            raise ValueError(f"{state} ({state_code}) not found in STAMM for service {service_key}")

        # Step 2: State → region level
        state_data = await self._get_json(state_link)
        links = state_data.get("gebietsliste", {}).get("links", [])

        # Check if any link is already a final page
        for link in links:
            if link.get("leistungsbeschreibung"):
                return f"{self.base_url}{link['url']}"

        # Try to find the right region by code, then by name, then fallback to first
        region_link = None
        if region_code:
            for link in links:
                if region_code in link.get("url", ""):
                    region_link = link["url"]
                    break

        if region_link is None:
            # Try name-based match
            for link in links:
                if city.lower() in link.get("name", "").lower():
                    region_link = link["url"]
                    break

        if region_link is None and links:
            region_link = links[0]["url"]
            logger.warning(
                "Region '%s' not found for %s/%s, using first available region",
                city, state, service_key,
            )

        if region_link is None:
            raise ValueError(f"No region found for city {city} in {state}")

        # Step 3: Walk region hierarchy until final page (max 5 levels)
        current_data = await self._get_json(region_link)
        for _ in range(5):
            current_links = current_data.get("gebietsliste", {}).get("links", [])

            for link in current_links:
                if link.get("leistungsbeschreibung"):
                    return f"{self.base_url}{link['url']}"

            if current_links:
                next_url = current_links[0]["url"]
                current_data = await self._get_json(next_url)
            else:
                break

        raise ValueError(f"Could not resolve final page for {service_key} in {city}, {state}")

    async def get_procedure(
        self, service_key: str, city: str = "Köln", state: str = "NRW"
    ) -> Procedure:
        """Fetch a procedure from SDG, using cache if available."""
        page_url = await self.resolve_final_page_url(service_key, city, state)

        # Check cache
        entry = cache.get(page_url)
        if entry is not None:
            proc = Procedure.model_validate_json(entry.normalized_json)
            if cache.is_stale(entry):
                proc.cache_stale = True
                proc.cached_at = entry.fetched_at
            return proc

        # Fetch live
        html = await self._get_html(page_url)
        proc = parse_sdg_page(html, source_url=page_url)

        # Cache it
        cache.set(page_url, html, proc.model_dump_json())
        return proc
