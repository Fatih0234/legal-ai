from __future__ import annotations

import sqlite3
from pathlib import Path

from app.schemas import CaseResult

DB_PATH = Path("data/cases.db")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cases "
        "(case_id TEXT PRIMARY KEY, result_json TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    conn.commit()
    return conn


def save(case_id: str, result: CaseResult) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cases VALUES (?, ?, datetime('now'))",
            (case_id, result.model_dump_json()),
        )


def get(case_id: str) -> CaseResult | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT result_json FROM cases WHERE case_id = ?", (case_id,)
    ).fetchone()
    conn.close()
    return CaseResult.model_validate_json(row[0]) if row else None
