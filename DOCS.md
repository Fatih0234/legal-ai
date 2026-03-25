# DOCS.md

## Core Product Docs

### MiniMax
- Compatible Anthropic API  
  https://platform.minimax.io/docs/api-reference/text-anthropic-api

### PydanticAI
- Home  
  https://ai.pydantic.dev/
- Agent  
  https://ai.pydantic.dev/agent/
- Dependencies  
  https://ai.pydantic.dev/dependencies/
- Tools  
  https://ai.pydantic.dev/tools/
- Common Tools  
  https://ai.pydantic.dev/common-tools/
- Multi-Agent Patterns  
  https://ai.pydantic.dev/multi-agent-applications/
- Anthropic Model Integration  
  https://ai.pydantic.dev/models/anthropic/

## Implementation Notes

### MiniMax via Anthropic SDK
Use MiniMax through Anthropic-compatible routing.

Environment shape:
```env
MINIMAX_API_KEY=...
MINIMAX_BASE_URL=https://api.minimax.io/anthropic
MINIMAX_MODEL=MiniMax-M2.7
```

Reference from MiniMax docs:
- Anthropic-compatible base URL:
  `https://api.minimax.io/anthropic`
- Supported message/content focus for this project:
  - text
  - tool_use
  - tool_result
  - thinking
- Current important limits:
  - image input not supported
  - document input not supported
  - append the full assistant response to history in multi-turn tool-call conversations

### PydanticAI integration shape
Use:
- `AnthropicModel`
- `AnthropicProvider`
- `deps_type`
- tool registration
- structured output

Suggested model factory:
```python
from anthropic import AsyncAnthropic
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

def build_model(api_key: str, base_url: str, model_name: str) -> AnthropicModel:
    client = AsyncAnthropic(api_key=api_key, base_url=base_url)
    provider = AnthropicProvider(anthropic_client=client)
    return AnthropicModel(model_name, provider=provider)
```

## Official Source Targets for MVP
- Federal service portal / Bundesportal
- Berlin service portal
- NRW economic service portal
- ELSTER
- DGUV
- Geoportal / GDI-DE
- GovData
- Gesetze im Internet

## Suggested Reading Order
1. MiniMax compatible Anthropic API
2. PydanticAI Anthropic integration
3. PydanticAI Agent
4. PydanticAI Dependencies
5. PydanticAI Tools
6. PydanticAI Multi-Agent Patterns

## Notes for the Coding Agent
- Keep the agent narrow.
- Prefer rule-based routing + MCP tool calls over agentic free-form planning.
- Use official sources only.
- Keep all normalized procedure objects source-backed.
- Do not automate filing in MVP.
