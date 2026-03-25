# PLAN.md — Implementation Tracker

Tracks progress across sessions. Source of truth for full spec: `TASK.md`.

## Phase 1: Project Init
- [x] `uv init` + add deps
- [x] Create directory structure
- [x] `.env.example`

## Phase 2: Schemas
- [x] `CaseProfile` (app/schemas.py)
- [x] `Procedure`
- [x] `ActionStep`
- [x] `RiskFlag`
- [x] `CaseResult`

## Phase 3: Rules Engine
- [x] `derive_flags(case)` in app/pipelines/rules.py
- [x] 5 flags: trade, food, ifsg, restaurant_permit, location_followup

## Phase 4: Static Adapters
- [x] bundesportal.py — trade reg, food reg, IfSG
- [x] berlin_service.py — restaurant permit, IHK
- [x] nrw_service.py — business reg
- [x] elster.py — tax registration step
- [x] dguv.py — DGUV registration step
- [x] geoportal.py — geo discovery sources

## Phase 5: Agent + MiniMax
- [x] config.py — env loading
- [x] prompts.py — system prompt
- [x] agent.py — build_model, AppDeps, Agent setup

## Phase 6: Orchestrator
- [x] orchestrator.py — validate → flags → adapters → merge → agent summary

## Phase 7: CLI
- [x] main.py — `python -m app.main case --json case.json`

## Phase 8: Tests
- [x] test_rules.py (5 tests)
- [x] test_adapters.py (18 tests)
- [x] test_e2e.py (3 scenarios + snapshot stability)
- [x] Test fixtures (3 case JSON files)
- [x] test_sdg.py (7 normalize + 5 live tests)

## Phase 9: Live SDG Scraping (NRW)
- [x] cache/sqlite.py — permanent SQLite cache
- [x] adapters/sdg_client.py — SDG API client, 5 req/s rate limit, hierarchical walk
- [x] pipelines/normalize.py — HTML accordion → Procedure parser
- [x] Orchestrator: evaluate_case_live() + gather_procedures_live()
- [x] CLI: `--live` flag
- [x] Live data works end-to-end with real SDG portal
