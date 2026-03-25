# Current App Report

As of March 25, 2026, this repository is a Python application that helps founders opening a cafe or small food business in Germany understand the main regulatory steps they need to take. The app combines a deterministic rules engine, a set of official-source adapters, a MiniMax-backed LLM summary layer, a Typer CLI, and a small FastAPI web UI with checklist progress tracking and follow-up chat.

## 1. Overall Product State

The app is beyond a skeleton. The main backend flow is implemented, the web UI exists, persistence is wired, and there is meaningful test coverage for the deterministic parts of the system.

At a high level, the app currently does this:

- accepts a structured business case
- derives rule flags from that case
- gathers procedures and action steps from static adapters or live SDG data
- builds a checklist with links, authorities, documents, and risk flags
- asks an LLM to generate a short summary and open questions
- persists the case, step progress, and chat history in SQLite

The product direction in the docs was originally "Berlin + NRW only", but the current implementation has already expanded beyond that in partial form. The UI and schema expose Bayern, Hamburg, Baden-Wuerttemberg, Hessen, Niedersachsen, and Sachsen in addition to Berlin and NRW.

## 2. Stack and Runtime

The project is managed with `uv` and targets Python 3.13+.

Main runtime dependencies:

- `fastapi` and `uvicorn` for the web API/UI
- `typer` and `rich` for the CLI
- `pydantic` and `pydantic-settings` for schemas and config
- `pydantic-ai-slim` plus `anthropic` for the LLM layer
- `httpx` for network access
- `beautifulsoup4` and `lxml` for HTML normalization
- `sqlite3` from the standard library for persistence

Important environment note:

- Running `pytest` directly in the machine Python failed because that interpreter did not have project dependencies installed.
- Running through `uv run ...` uses the intended project environment and is the correct way to execute the app and tests.

Configuration is loaded from `.env` through `app/config.py`. The app is currently configured for MiniMax via the Anthropic-compatible endpoint:

- `MINIMAX_BASE_URL=https://api.minimax.io/anthropic`
- `MINIMAX_MODEL=MiniMax-M2.7`

During inspection, the MiniMax API key was present in the local environment.

## 3. Main Application Architecture

The current architecture is simple and readable:

### 3.1 Schemas

`app/schemas.py` defines the core models:

- `CaseProfile` for input
- `Procedure`, `ActionStep`, and `RiskFlag` for normalized data
- `CaseFlags` for derived rule decisions
- `CaseResult` for the final assembled result

This is the main domain contract for both CLI and web output.

### 3.2 Rules Layer

`app/pipelines/rules.py` contains the deterministic business rules. Right now the rules are intentionally narrow:

- always require trade registration
- always require food business registration
- require IfSG instruction when employees handle food
- require restaurant permit path when alcohol is served
- flag location follow-up when the premises were not previously gastronomy

This layer is small, easy to reason about, and well covered by tests.

### 3.3 Orchestration Layer

`app/orchestrator.py` is the core of the app.

It has three main responsibilities:

1. gather procedures and actions
2. build the checklist
3. enrich that deterministic output with an LLM-generated summary and open questions

There are two modes:

- `evaluate_case`: static adapter mode
- `evaluate_case_live`: live SDG mode for non-Berlin procedure lookups

The deterministic part of the app is clearly separated from the agent layer, which is a good design choice. It means the core checklist logic is still usable even when the model fails.

## 4. Data Sources and Adapters

The app uses a mixed adapter strategy.

### 4.1 Static Adapters

Static procedure/action adapters exist for:

- Bundesportal
- Berlin service portal
- NRW service portal
- ELSTER
- DGUV
- Geoportal / location risks
- a generic fallback service for non-Berlin, non-NRW restaurant permit handling

These adapters mostly return normalized `Procedure` or `ActionStep` objects with fixed text and official URLs.

### 4.2 Live SDG Adapter

`app/adapters/sdg_client.py` is the most dynamic adapter in the codebase.

It currently:

- resolves SDG hierarchy endpoints to a final procedure page
- supports `trade`, `food`, and `ifsg`
- rate-limits requests
- fetches HTML pages
- normalizes them into `Procedure` objects
- caches raw HTML and normalized JSON in SQLite

`app/pipelines/normalize.py` parses the SDG accordion sections into structured data. This is one of the more implementation-heavy parts of the app and appears to be covered by parser tests plus optional live tests.

### 4.3 State Support Status

The current state support is mixed:

- Berlin: strongest support in static mode
- NRW: strong support in static mode and live mode
- Bayern, Hamburg, Baden-Wuerttemberg, Hessen, Niedersachsen, Sachsen: partially exposed in schema/UI and partly supported by live SDG routing

Important limitation:

- In static mode, all non-Berlin trade registration currently goes through the NRW business registration adapter. That means static-mode support outside Berlin/NRW is not truly state-specific yet.
- In live mode, non-Berlin states are handled more realistically for trade, food, and IfSG through the SDG client.
- Restaurant permit handling outside Berlin/NRW falls back to the generic adapter.

Region code coverage is uneven:

- NRW has 10 mapped cities
- Bayern has 6 mapped cities
- Hamburg has 1 mapped city
- Baden-Wuerttemberg, Hessen, Niedersachsen, and Sachsen currently rely on fallback matching rather than explicit regional mappings

## 5. LLM and Agent Layer

The app has two separate agent experiences:

- `legal_agent` for generating the final summary and open questions
- `chat_agent` for follow-up Q&A

The LLM integration is narrow by design:

- the checklist is built deterministically first
- the model is only asked to summarize and identify follow-up questions
- the chat agent is tool-enabled and can fetch procedure details through local adapter tools

This is a good current-state architecture because it limits hallucination risk compared with a model-driven planner.

Important operational detail:

- `evaluate_case` and `evaluate_case_live` catch agent failures and still return a usable checklist with a fallback summary message
- `/api/chat` does not degrade the same way; it returns HTTP 500 if the model/tool call fails

That means the checklist path is more resilient than the chat path right now.

## 6. Interfaces Exposed Today

### 6.1 CLI

The Typer CLI supports:

- default evaluation flow via `python -m app.main --json case.json`
- `web` command to start FastAPI
- `chat` command to open interactive terminal chat

The CLI renders:

- summary
- must-do actions
- conditional steps
- risk flags
- open questions
- official links
- full JSON output

Current mismatch:

- older planning docs refer to a `case` subcommand, but the implemented CLI uses the callback as the default command instead.

### 6.2 Web App

The web layer is a single FastAPI app serving one HTML page plus JSON APIs.

Exposed routes:

- `GET /`
- `POST /api/evaluate`
- `GET /api/cases/{case_id}`
- `GET /api/cases/{case_id}/progress`
- `PATCH /api/cases/{case_id}/steps/{step_key}`
- `POST /api/chat`
- `DELETE /api/chat/{session_id}`
- `GET /health`

The frontend is a single large `templates/index.html` file with inline CSS and JS. There is no frontend build step, no separate asset pipeline, and no client framework.

### 6.3 Current UI Behavior

The web UI currently includes:

- input form for state, city, address, legal form, and operational flags
- results sections for summary, must-do items, conditional steps, risks, authorities, links, and open questions
- progress controls for marking steps as `PENDING`, `DONE`, or `BLOCKED`
- embedded follow-up chat
- expandable raw JSON output

The UI is styled and intentionally designed rather than barebones. It is not just a test harness.

Important UI limitation:

- the backend `EvaluateRequest` supports `live: bool`
- the frontend form does not send a `live` field
- result: live mode exists in the API and CLI, but not in the web UI

Another mismatch:

- the CLI startup message advertises a `/chat` page
- the FastAPI app does not expose `/chat`
- chat currently exists inside the main `/` page and as `/api/chat`

## 7. Persistence and Local Data

Persistence is simple and local.

### 7.1 SQLite Databases

The app currently uses:

- `data/cases.db`
- `data/cache.db`

`data/cases.db` contains:

- `cases`
- `chat_sessions`
- `progress`

`data/cache.db` contains:

- `cache`

### 7.2 What Gets Stored

The app currently persists:

- full evaluated case results
- chat message history per session
- progress status per checklist step
- cached SDG HTML and normalized procedure JSON

### 7.3 Local Snapshot During Inspection

On March 25, 2026, the local databases contained:

- `cases`: 13 rows
- `chat_sessions`: 2 rows
- `progress`: 57 rows
- `cache`: 4 rows

This is environment-specific local data, not application seed data.

## 8. Validation and Domain Constraints

Input validation is present but not complete.

Current constraints:

- `state` must match the enum values in `CaseProfile`
- `legal_form` must match allowed enum values
- some city validation exists via `REGION_CODES`

Important nuance:

- city validation only applies when a state has a non-empty mapped city list
- states with empty region maps effectively skip strict city validation
- Berlin currently has no explicit region map entry, so Berlin city validation is not enforced in the same way as NRW

This is acceptable for a current MVP, but it means input quality varies by state.

## 9. Testing and Verified Status

The test suite is meaningful and split into sensible layers:

- `tests/test_rules.py`
- `tests/test_adapters.py`
- `tests/test_e2e.py`
- `tests/test_sdg.py`
- `tests/test_web.py`

### 9.1 What Was Verified

Using `uv run pytest -m 'not live'`:

- adapter tests passed
- rules tests passed
- deterministic end-to-end checklist tests passed
- SDG parser tests passed

The non-live suite clearly executed through:

- `tests/test_adapters.py`
- `tests/test_e2e.py`
- `tests/test_rules.py`
- `tests/test_sdg.py`

### 9.2 What Remains Operationally Sensitive

The web tests began successfully and at least the early route checks passed, but evaluation/chat-related web tests were slower because those paths rely on the live LLM-backed summary/chat flow.

That points to an important current-state property of the app:

- deterministic backend logic is stable and testable
- full web evaluation and chat behavior still depend on external model latency/availability

There are also live SDG tests in `tests/test_sdg.py`, which means part of the verification story is intentionally network-dependent.

## 10. Main Strengths Right Now

The current codebase is strongest in these areas:

- clear backend structure
- deterministic core flow before LLM summarization
- usable web UI with persistence and progress tracking
- real adapter layer rather than a mock-only prototype
- local caching for brittle or expensive SDG lookups
- test coverage around the rules and checklist assembly

This is already a functioning application shape, not just an experiment.

## 11. Main Gaps and Risks Right Now

The main current gaps are:

### 11.1 Product Scope vs Implementation Drift

The docs still describe a Berlin/NRW MVP, but the code and UI now expose broader state coverage. That creates ambiguity about what is officially supported versus only partially supported.

### 11.2 Static Mode Is Not Fully State-Aware

Static mode still routes every non-Berlin trade registration through the NRW adapter. That is a shortcut, not true nationwide support.

### 11.3 Live Mode Is Not Exposed in the UI

The feature exists in API and CLI, but a web user cannot turn it on from the form.

### 11.4 LLM Dependency Is Unevenly Handled

- checklist generation degrades gracefully when the agent fails
- chat does not degrade gracefully and can fail the request outright

### 11.5 Frontend Is Monolithic

The web app is all inline in a single `index.html`. That is fine for an MVP, but it will get harder to maintain as UI behavior grows.

### 11.6 No Auth / Multi-User Isolation

Everything is local and anonymous. There is no user model, no auth, and no separation beyond generated case/session IDs.

### 11.7 Route and Docs Mismatches

Current examples:

- CLI docs/plans mention a `case` subcommand that does not exist
- the web command prints a `/chat` URL that is not implemented

## 12. Current Main Parts Summary

If someone asked "what are the main parts of the app today?", the answer is:

1. Input and domain modeling
   The Pydantic schema layer defines the business case, normalized procedures, action steps, risk flags, and final output.

2. Deterministic compliance engine
   The rules engine and orchestrator build the actual checklist from structured inputs and official-source adapters.

3. Official-source adapter layer
   Static and live adapters pull or represent procedures from Bundesportal, Berlin, NRW, ELSTER, DGUV, and SDG.

4. LLM enrichment layer
   MiniMax via the Anthropic-compatible SDK is used for summary generation and follow-up chat, but not for primary decision logic.

5. User interfaces
   A Typer CLI and a FastAPI web app expose the functionality.

6. Persistence and cache
   SQLite stores case results, chat sessions, progress state, and SDG cache entries.

7. Verification
   The repo has a practical test suite, with deterministic tests in good shape and some live/integration behavior dependent on external services.

## 13. Practical Assessment

The app is currently in a solid MVP-plus state:

- more than a prototype
- not yet a hardened production system
- strongest in deterministic checklist generation
- weaker in consistency around nationwide support, UI exposure of live mode, and external-dependency handling

If development continued from here, the highest-value next moves would be:

- align product docs with actual supported states and modes
- expose live mode in the UI
- separate or stub model-dependent web tests
- make chat degrade gracefully like evaluation does
- replace NRW-specific static fallbacks for other states with proper state-aware adapters or explicit unsupported-state handling

## 14. Bottom Line

Today the app is a working regulatory checklist generator with:

- a clear backend architecture
- real source-backed procedure handling
- a usable web experience
- persisted case and chat state
- test coverage on the deterministic core

The main thing holding it back from feeling fully production-ready is not missing architecture. It is the remaining gap between the narrowed MVP design and the broader, partially implemented support now exposed by the code and UI.
