"""Model Router — Routes LLM calls to optimal model by task type."""
import os
from typing import Optional

ROUTING_TABLE = {
    "triage": "fast",
    "classification": "fast",
    "entity_extraction": "fast",
    "complex_reasoning": "powerful",
    "sar_generation": "powerful",
    "risk_assessment": "powerful",
    "narrative": "powerful",
    "reflection": "powerful",
}

MODEL_TIERS = {
    "fast": {
        "anthropic": "claude-haiku-4-5-20251001",
        "openai": "gpt-4o-mini",
    },
    "powerful": {
        "anthropic": "claude-sonnet-4-20250514",
        "openai": "gpt-4o",
    },
}


def get_provider() -> Optional[str]:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None


def route_model(task_type: str) -> Optional[str]:
    """Get the optimal model name for a given task type."""
    tier = ROUTING_TABLE.get(task_type, "powerful")
    provider = get_provider()
    if not provider:
        return None
    return MODEL_TIERS[tier].get(provider)


def get_routed_llm(task_type: str):
    """Get an LLM instance routed by task type."""
    provider = get_provider()
    if not provider:
        return None

    tier = ROUTING_TABLE.get(task_type, "powerful")
    model_name = MODEL_TIERS[tier][provider]

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=model_name, temperature=0.0, max_tokens=1024)
        except ImportError:
            return None
    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model_name, temperature=0.0, max_tokens=1024)
        except ImportError:
            return None

    return None
