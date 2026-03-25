from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class State(str, Enum):
    BERLIN = "Berlin"
    NRW = "NRW"


class LegalForm(str, Enum):
    SOLE_PROPRIETOR = "sole proprietor"
    UG = "UG"
    GMBH = "GmbH"


class CaseProfile(BaseModel):
    state: State
    city: str
    address: str = ""
    business_type: str = "cafe"
    serves_alcohol: bool = False
    has_seating: bool = True
    takeaway_only: bool = False
    existing_gastro_premises: bool = False
    employees_handle_food: bool = True
    founder_handles_food: bool = True
    legal_form: LegalForm = LegalForm.SOLE_PROPRIETOR

    @model_validator(mode="after")
    def validate_city_for_state(self) -> "CaseProfile":
        from app.adapters.regions import REGION_CODES

        known = REGION_CODES.get(self.state.value, {})
        if known and self.city not in known:
            supported = ", ".join(known)
            raise ValueError(
                f"City '{self.city}' is not supported for {self.state.value}. "
                f"Supported cities: {supported}"
            )
        return self


class Procedure(BaseModel):
    title: str
    description: str = ""
    steps: list[str] = Field(default_factory=list)
    source_url: str = ""
    source_name: str = ""
    last_checked_at: str = ""
    state_specific: bool = False
    category: str = ""
    cache_stale: bool = False
    cached_at: str = ""


class ActionStep(BaseModel):
    title: str
    description: str = ""
    action_url: str = ""
    action_type: Literal["registration", "filing", "notification", "insurance"] = (
        "registration"
    )
    source_url: str = ""
    last_checked_at: str = ""


class RiskFlag(BaseModel):
    category: str
    description: str
    severity: Literal["info", "warning", "critical"] = "info"
    recommendation: str = ""
    source_url: str = ""


class CaseFlags(BaseModel):
    needs_trade_registration: bool = True
    needs_food_registration: bool = True
    needs_ifsg: bool = False
    needs_restaurant_permit: bool = False
    needs_ihk_instruction: bool = False
    needs_commercial_register: bool = False
    needs_location_followup: bool = False


class CaseResult(BaseModel):
    summary: str = ""
    must_do_now: list[str] = Field(default_factory=list)
    conditional_steps: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    authorities: list[str] = Field(default_factory=list)
    official_links: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    procedures: list[Procedure] = Field(default_factory=list)
    action_steps: list[ActionStep] = Field(default_factory=list)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    flags: CaseFlags = Field(default_factory=CaseFlags)
    stale_cache_warnings: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(tz=UTC).isoformat())
