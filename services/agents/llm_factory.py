"""
BYOK (Bring Your Own Key) LLM Factory.

Supports Anthropic and OpenAI via LangChain interfaces.
Falls back to None when no API key is configured — agents
degrade gracefully to heuristic-only mode.
"""
import os
from typing import Optional

from core.utils.logging import get_logger

logger = get_logger(__name__)


def get_llm(model: str = "default", temperature: float = 0.0) -> Optional[object]:
    """
    Get an LLM instance based on available API keys.

    Priority: ANTHROPIC_API_KEY > OPENAI_API_KEY > None (heuristic fallback)
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key:
        try:
            from langchain_anthropic import ChatAnthropic
            model_name = "claude-sonnet-4-20250514" if model == "default" else model
            llm = ChatAnthropic(
                model=model_name,
                temperature=temperature,
                api_key=anthropic_key,
            )
            logger.info("LLM initialized", provider="anthropic", model=model_name)
            return llm
        except ImportError:
            logger.warning("langchain-anthropic not installed, trying OpenAI")
        except Exception as e:
            logger.error("Failed to initialize Anthropic LLM", error=str(e))

    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            model_name = "gpt-4o" if model == "default" else model
            llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=openai_key,
            )
            logger.info("LLM initialized", provider="openai", model=model_name)
            return llm
        except ImportError:
            logger.warning("langchain-openai not installed")
        except Exception as e:
            logger.error("Failed to initialize OpenAI LLM", error=str(e))

    logger.info("No LLM API key configured — agents will use heuristic mode")
    return None


def is_llm_available() -> bool:
    """Check if any LLM provider is configured."""
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))
