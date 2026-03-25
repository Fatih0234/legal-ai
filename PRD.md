# PRD.md

## Product
Germany Café Navigator

## Objective
Help a founder opening a café / small food business in **Berlin** or **NRW** understand:
- what they must do
- what depends on alcohol / premises / staff
- which authority is relevant
- which official link is next

## User
- founder / operator
- small team
- not a lawyer
- needs a short actionable checklist

## Input
```json
{
  "state": "Berlin | NRW",
  "city": "string",
  "address": "string",
  "business_type": "cafe",
  "serves_alcohol": true,
  "has_seating": true,
  "takeaway_only": false,
  "existing_gastro_premises": false,
  "employees_handle_food": true,
  "legal_form": "sole proprietor | UG | GmbH"
}
```

## Output
```json
{
  "summary": "string",
  "must_do_now": ["..."],
  "conditional_steps": ["..."],
  "documents": ["..."],
  "authorities": ["..."],
  "official_links": ["..."],
  "open_questions": ["..."]
}
```

## In Scope
- trade registration
- food business registration
- infection protection instruction branch
- alcohol permit branch
- ELSTER tax registration step
- DGUV registration step
- zoning / change-of-use risk flag
- Berlin + NRW only

## Out of Scope
- automated filing
- nationwide support
- legal advice beyond official source synthesis
- full building permit workflow

## Functional Requirements
1. Accept structured case input.
2. Run a rule-based decision tree.
3. Query MCP tools for official procedures.
4. Return a short checklist with official links.
5. Never invent permits or requirements.
6. Clearly label uncertainty or municipality-dependent items.
7. Persist source URL and `last_checked_at` for every normalized procedure.

## Core Rules
- always include trade registration
- always include food business registration
- include IfSG instruction if food-handling staff are involved
- include restaurant permit path if alcohol is served
- include ELSTER step
- include DGUV step
- flag premises risk if not an existing gastronomy location

## Non-Functional Requirements
- Python project managed with `uv`
- typed code
- modular adapters
- JSON-first output
- source allowlist only
- local cache for fetched pages
- easy handoff to later UI / voice layer

## Success Criteria
- Case output is generated in under 10 seconds with warm cache
- At least 90% of output items include an official source URL
- Same case input produces stable output
- Berlin and NRW happy-path cases covered by tests

## Architecture
- `orchestrator`: intake -> rules -> MCP calls -> merge -> output
- `procedure_mcp`: main official-procedure source
- `action_mcp`: tax / DGUV / checklist / draft email
- `location_mcp`: geo / municipal source discovery + risk flag
- `law_mcp`: legal basis lookup only

## Model Harness
Use **MiniMax through the Anthropic SDK compatibility layer** and wire it into **PydanticAI's Anthropic model/provider** using a custom Anthropic client or equivalent provider configuration.
