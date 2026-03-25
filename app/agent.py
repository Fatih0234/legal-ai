from __future__ import annotations

from dataclasses import dataclass

import httpx
from anthropic import AsyncAnthropic
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from app.config import settings
from app.prompts import SYSTEM_PROMPT


@dataclass
class AppDeps:
    http_client: httpx.AsyncClient


class AgentOutput(BaseModel):
    summary: str
    open_questions: list[str]


def build_model(
    api_key: str = "",
    base_url: str = "",
    model_name: str = "",
) -> AnthropicModel:
    api_key = api_key or settings.minimax_api_key
    base_url = base_url or settings.minimax_base_url
    model_name = model_name or settings.minimax_model

    client = AsyncAnthropic(api_key=api_key, base_url=base_url)
    provider = AnthropicProvider(anthropic_client=client)
    return AnthropicModel(model_name, provider=provider)


legal_agent = Agent[AppDeps, AgentOutput](
    build_model(),
    deps_type=AppDeps,
    output_type=AgentOutput,
    instructions=SYSTEM_PROMPT,
    model_settings={"temperature": 0.1},
)
