from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.agent import AppDeps
from app.chat_agent import chat_agent
from app.schemas import CaseProfile, CaseResult
from app.store import cases as cases_store
from app.store import progress as progress_store
from app.store import sessions as sessions_store

logger = logging.getLogger(__name__)

app = FastAPI(title="Germany Café Navigator")

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@app.get("/", response_class=HTMLResponse)
async def form_page():
    return (TEMPLATES_DIR / "index.html").read_text()


class EvaluateRequest(BaseModel):
    state: str
    city: str
    address: str = ""
    business_type: str = "cafe"
    serves_alcohol: bool = False
    has_seating: bool = True
    takeaway_only: bool = False
    existing_gastro_premises: bool = False
    employees_handle_food: bool = True
    legal_form: str = "sole proprietor"
    live: bool = False


@app.post("/api/evaluate")
async def evaluate_case(req: EvaluateRequest):
    try:
        case = CaseProfile.model_validate(req.model_dump())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    if req.live:
        from app.orchestrator import evaluate_case_live

        result = await evaluate_case_live(case)
    else:
        from app.orchestrator import evaluate_case

        result = await evaluate_case(case)

    case_id = uuid.uuid4().hex[:8]
    cases_store.save(case_id, result)

    # Initialise progress tracker for all checklist steps
    all_steps = (
        result.must_do_now
        + result.conditional_steps
        + [s.title for s in result.action_steps]
    )
    progress_store.init_case(case_id, all_steps)

    result_dict = result.model_dump()
    result_dict["case_id"] = case_id
    return result_dict


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    result = cases_store.get(case_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return result.model_dump()


@app.get("/api/cases/{case_id}/progress")
async def get_progress(case_id: str):
    return progress_store.get_all(case_id)


class StepStatusRequest(BaseModel):
    status: str  # PENDING | DONE | BLOCKED


@app.patch("/api/cases/{case_id}/steps/{step_key}")
async def update_step(case_id: str, step_key: str, req: StepStatusRequest):
    valid = {"PENDING", "DONE", "BLOCKED"}
    if req.status not in valid:
        raise HTTPException(status_code=422, detail=f"status must be one of {valid}")
    updated = progress_store.upsert(case_id, step_key, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Step not found")
    return {"ok": True}


def _chat_fallback(case_id: str) -> str:
    if case_id:
        result = cases_store.get(case_id)
        if result and result.must_do_now:
            steps = "\n".join(f"• {s}" for s in result.must_do_now)
            return (
                "I'm temporarily unavailable. "
                "Based on your evaluation, your key action items are:\n\n"
                f"{steps}\n\n"
                "Please refer to the full checklist above for details."
            )
    return (
        "I'm temporarily unavailable. "
        "Please refer to your checklist above or try again later."
    )


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""
    case_id: str = ""


@app.post("/api/chat")
async def chat(req: ChatRequest):
    import httpx
    from pydantic_ai.messages import ModelMessagesTypeAdapter

    # Resolve or create session
    session_id = req.session_id or uuid.uuid4().hex[:12]

    # Load existing history
    history = []
    raw = sessions_store.load(session_id)
    if raw:
        try:
            history = ModelMessagesTypeAdapter.validate_json(raw)
        except Exception:
            history = []

    deps = AppDeps(http_client=httpx.AsyncClient())
    try:
        result = await chat_agent.run(
            req.message, message_history=history, deps=deps
        )
        # Persist updated history
        sessions_store.save(session_id, ModelMessagesTypeAdapter.dump_json(result.all_messages()))
        return {"response": result.output, "session_id": session_id}
    except Exception as exc:
        logger.error("Chat agent failed: %s", exc)
        fallback = _chat_fallback(req.case_id)
        return {"response": fallback, "session_id": session_id}


@app.delete("/api/chat/{session_id}")
async def clear_chat(session_id: str):
    sessions_store.delete(session_id)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok"}
