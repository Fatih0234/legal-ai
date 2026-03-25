from __future__ import annotations

# SDG portal 2-letter state codes (Länderkennzeichen)
STATE_CODES: dict[str, str] = {
    "Berlin": "BE",
    "NRW": "NW",
}

# City → SDG region code per state.
# NRW uses Regierungsbezirk codes; city-states use the state-level code.
# For states where codes are unknown, leave empty — the SDG client falls back to
# name-based matching, then to the first available region.
REGION_CODES: dict[str, dict[str, str]] = {
    "NRW": {
        "Köln": "053000000000",
        "Düsseldorf": "051000000000",
        "Dortmund": "055000000000",
        "Münster": "059000000000",
        "Arnsberg": "055000000000",
        "Bielefeld": "057000000000",
        "Bonn": "053000000000",
        "Wuppertal": "051000000000",
        "Bochum": "055000000000",
        "Essen": "051000000000",
    },
}

# Backward-compatibility alias used by legacy imports
NRW_REGION_CODES = REGION_CODES["NRW"]
