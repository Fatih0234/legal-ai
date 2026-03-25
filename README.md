# Germany Café Navigator

Regulatory checklist generator for founders opening a café or small food business in Germany.

---

## What it does

Given a structured description of your planned business, the app:

1. Applies a deterministic rules engine to derive which registrations, permits, and compliance steps apply to your situation.
2. Pulls procedure details from official-source adapters (Bundesportal, Berlin service portal, NRW service portal, ELSTER, DGUV) or live from the Single Digital Gateway (SDG) portal.
3. Assembles a checklist with action steps, authority contacts, official links, and risk flags.
4. Asks an LLM to produce a short plain-language summary and a list of open questions — but the LLM does not drive the checklist logic, only the narrative layer.
5. Persists case results, step progress, and chat history in a local SQLite database.

---

## Supported states

| State | Static mode | Live mode |
|-------|-------------|-----------|
| Berlin | Full static adapter coverage | — |
| NRW (Nordrhein-Westfalen) | Full static adapter coverage | SDG lookup for trade, food, IfSG |

Only Berlin and NRW are supported. The app will reject input for any other state.

NRW city validation is strict: only the ten mapped cities are accepted (Köln, Düsseldorf, Dortmund, Münster, Arnsberg, Bielefeld, Bonn, Wuppertal, Bochum, Essen). Berlin accepts any city string.

---

## Static mode vs live mode

**Static mode** (default) uses pre-mapped procedure data baked into the adapters. Responses are fast and work offline. The data reflects official sources as of the last time the adapters were updated.

**Live mode** (`--live` CLI flag or `"live": true` in the API request body) fetches and caches current procedure pages from the SDG portal. Live mode is currently useful for NRW trade, food, and IfSG procedures. It is slower and requires a network connection. Results are cached in `data/cache.db`.

Live mode is exposed via the CLI and the `POST /api/evaluate` endpoint. The web form does not currently offer a live mode toggle.

---

## Official sources used

- [Bundesportal](https://www.bundesportal.de) — federal trade registration (Gewerbeanmeldung)
- [Berlin service portal](https://service.berlin.de) — Berlin-specific food, alcohol, and location procedures
- [NRW service portal](https://www.nrw.de) — NRW-specific trade registration and food business procedures
- [ELSTER](https://www.elster.de) — tax registration
- [DGUV](https://www.dguv.de) — employers' liability insurance (Berufsgenossenschaft)
- [SDG portal](https://sdg.digitalservicebund.de) — live procedure data for NRW in live mode

---

## What the app does not do

- It does not provide legal advice. Output is informational only.
- It does not submit any registration or application on your behalf.
- It does not cover states other than Berlin and NRW.
- It does not model all possible business types — coverage is focused on cafés, small restaurants, and takeaway operations.
- It does not handle GbR, AG, or other legal forms beyond sole proprietor, UG, and GmbH.
- It does not check zoning, building permits, or noise regulations.
- It does not verify real-time authority contact details or fee schedules.

---

## Known limitations

- **Static data can go stale.** Adapter URLs and procedure descriptions reflect a fixed snapshot. Use live mode for NRW if you need current SDG data.
- **Chat path is not fault-tolerant.** The evaluation checklist degrades gracefully when the LLM is unavailable. The follow-up chat (`POST /api/chat`) does not — it returns HTTP 500 if the model call fails.
- **No authentication.** The app is single-user and local. There is no user model, session auth, or access control.
- **LLM provider is configurable but assumed to be available.** The summary and chat layers require a working API key set in `.env` (`MINIMAX_BASE_URL`, `MINIMAX_MODEL`). Without it, the LLM layer is skipped and a fallback message is shown in the checklist; chat is unavailable.

---

## Running the app

Requires Python 3.13+ and [uv](https://github.com/astral-sh/uv).

```bash
# Install dependencies
uv sync

# Run evaluation from a JSON case file
uv run python -m app.main --json case.json

# Run with live SDG data (NRW)
uv run python -m app.main --json case.json --live

# Start the web UI
uv run python -m app.main web

# Start interactive terminal chat
uv run python -m app.main chat
```

The web UI is available at `http://127.0.0.1:8000/` after starting the server.

### Example case file

```json
{
  "state": "Berlin",
  "city": "Berlin",
  "business_type": "cafe",
  "serves_alcohol": false,
  "has_seating": true,
  "takeaway_only": false,
  "existing_gastro_premises": false,
  "employees_handle_food": true,
  "legal_form": "sole proprietor"
}
```

Valid values: `state` → `Berlin` or `NRW`; `legal_form` → `sole proprietor`, `UG`, or `GmbH`.

---

## Running tests

```bash
# Deterministic tests only (no network)
uv run pytest -m 'not live'

# All tests including live SDG calls
uv run pytest
```
