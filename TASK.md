# TASK.md

## Setup
- [ ] Initialize project with `uv`
- [ ] Add dependencies:
  - [ ] `pydantic`
  - [ ] `pydantic-ai-slim[anthropic]`
  - [ ] `anthropic`
  - [ ] `httpx`
  - [ ] `beautifulsoup4`
  - [ ] `lxml`
  - [ ] `typer`
  - [ ] `rich`
  - [ ] `fastapi`
  - [ ] `uvicorn`
  - [ ] `pytest`

## Repo
- [ ] Create:
```text
app/
  main.py
  config.py
  schemas.py
  prompts.py
  orchestrator.py
  adapters/
    bundesportal.py
    berlin_service.py
    nrw_service.py
    elster.py
    dguv.py
    geoportal.py
    govdata.py
  mcp/
    law_server.py
    procedure_server.py
    action_server.py
    location_server.py
  pipelines/
    intake.py
    rules.py
    normalize.py
    checklist.py
  cache/
    sqlite.py
tests/
```

## Config
- [ ] Add `.env.example`
```env
MINIMAX_API_KEY=
MINIMAX_BASE_URL=https://api.minimax.io/anthropic
MINIMAX_MODEL=MiniMax-M2.7
APP_ENV=dev
HTTP_TIMEOUT=30
```

## Schemas
- [ ] Implement `CaseProfile`
- [ ] Implement `Procedure`
- [ ] Implement `ActionStep`
- [ ] Implement `RiskFlag`
- [ ] Implement final `CaseResult`

## Rules
- [ ] Implement `derive_flags(case: CaseProfile)`
- [ ] Flags:
  - [ ] `needs_trade_registration`
  - [ ] `needs_food_registration`
  - [ ] `needs_ifsg`
  - [ ] `needs_restaurant_permit`
  - [ ] `needs_location_followup`

## Adapters
- [ ] `bundesportal.py`
  - [ ] fetch trade registration page
  - [ ] fetch food registration page
  - [ ] fetch infection protection page
  - [ ] normalize sections into `Procedure`
- [ ] `berlin_service.py`
  - [ ] fetch restaurant permit page
  - [ ] fetch gastronomy instruction / IHK page
  - [ ] normalize into `Procedure`
- [ ] `nrw_service.py`
  - [ ] fetch business registration page
  - [ ] normalize into `Procedure`
- [ ] `elster.py`
  - [ ] create `ActionStep` for tax registration
- [ ] `dguv.py`
  - [ ] create `ActionStep` for DGUV registration
- [ ] `geoportal.py`
  - [ ] return geo discovery sources only
- [ ] `govdata.py`
  - [ ] optional lookup helper for open municipal datasets

## MCP Servers
- [ ] `procedure_server.py`
  - [ ] `get_trade_registration(state, city)`
  - [ ] `get_food_business_registration(state, city)`
  - [ ] `get_ifsg_instruction(state, city)`
  - [ ] `get_restaurant_permit(state, city, serves_alcohol)`
  - [ ] `get_ihk_instruction(state, city, serves_alcohol)`
- [ ] `action_server.py`
  - [ ] `get_tax_registration_step(legal_form)`
  - [ ] `get_dguv_registration_step()`
  - [ ] `generate_founder_checklist(case_profile, procedures)`
  - [ ] `draft_authority_email(case_profile, target)`
- [ ] `location_server.py`
  - [ ] `find_geo_sources(state, city)`
  - [ ] `find_municipal_service_sources(state, city)`
  - [ ] `flag_location_risk(existing_gastro_premises)`
- [ ] `law_server.py`
  - [ ] `search_law(query)`
  - [ ] `get_law_text(law_id, section=None)`
  - [ ] `extract_legal_basis(topic)`

## PydanticAI Harness
- [ ] Create dependency container:
```python
from dataclasses import dataclass
import httpx

@dataclass
class AppDeps:
    http_client: httpx.AsyncClient
```
- [ ] Create model factory:
```python
from anthropic import AsyncAnthropic
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

def build_model(api_key: str, base_url: str, model_name: str) -> AnthropicModel:
    client = AsyncAnthropic(api_key=api_key, base_url=base_url)
    provider = AnthropicProvider(anthropic_client=client)
    return AnthropicModel(model_name, provider=provider)
```
- [ ] Create agent with:
  - [ ] strict instructions
  - [ ] dependency type
  - [ ] output schema
  - [ ] MCP tool registration
- [ ] Ensure full assistant messages remain in history across tool-call turns

## Orchestrator
- [ ] Validate input
- [ ] Derive flags
- [ ] Call MCP tools based on flags
- [ ] Merge procedures + action steps + risk flags
- [ ] Return `CaseResult`

## CLI
- [ ] `python -m app.main case --json case.json`
- [ ] `python -m app.main chat`
- [ ] `python -m app.main refresh-sources`

## API
- [ ] `POST /cases/evaluate`
- [ ] `POST /sources/refresh`
- [ ] `GET /health`

## Caching
- [ ] store raw HTML
- [ ] store normalized JSON
- [ ] store `fetched_at`
- [ ] add manual override support for brittle selectors

## Tests
- [ ] rules unit tests
- [ ] procedure normalization tests
- [ ] Berlin no-alcohol happy path
- [ ] Berlin alcohol + new premises
- [ ] NRW takeaway variant
- [ ] stable JSON snapshot tests

## Acceptance Criteria
- [ ] Same input -> same output
- [ ] Every checklist item includes a source URL where available
- [ ] Unknown municipality-specific items are labeled as unresolved
- [ ] No invented requirements in tests
