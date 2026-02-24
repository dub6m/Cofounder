"""
LLM Router — dispatches requests to the correct provider based on role.
- Cofounder: Cerebras SDK (AsyncCerebras) → gpt-oss-120b
- Architect: OpenAI AsyncOpenAI → gpt-4.1-nano
- Executor:  OpenAI-compatible AsyncOpenAI → SiliconFlow Qwen2.5-Coder-7B

Implements exponential backoff for rate-limited providers.
"""

import asyncio
import logging
from enum import Enum
from typing import AsyncGenerator

from cerebras.cloud.sdk import AsyncCerebras
from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)


class LlmRole(str, Enum):
    COFOUNDER = "cofounder"       # Cerebras gpt-oss-120b
    ARCHITECT = "architect"       # OpenAI GPT-4.1-Nano
    EXECUTOR = "executor"         # SiliconFlow Qwen2.5-Coder-7B


# ── Singleton clients (lazy init) ─────────────────────────────

_cerebrasClient: AsyncCerebras | None = None
_openaiClient: AsyncOpenAI | None = None
_siliconflowClient: AsyncOpenAI | None = None


def _getCerebrasClient() -> AsyncCerebras:
    global _cerebrasClient
    if _cerebrasClient is None:
        _cerebrasClient = AsyncCerebras(
            api_key=settings.cerebras_api_key,
        )
    return _cerebrasClient


def _getOpenaiClient() -> AsyncOpenAI:
    global _openaiClient
    if _openaiClient is None:
        _openaiClient = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openaiClient


def _getSiliconflowClient() -> AsyncOpenAI:
    global _siliconflowClient
    if _siliconflowClient is None:
        _siliconflowClient = AsyncOpenAI(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
        )
    return _siliconflowClient


# ── Chat Completion ────────────────────────────────────────────

async def chatCompletion(
    role: LlmRole,
    messages: list[dict],
    temperature: float = 0.7,
    maxTokens: int = 4096,
    retries: int = 3,
) -> str:
    """
    Non-streaming chat completion with exponential backoff.
    Returns the full assistant message content.
    """
    backoff = settings.siliconflow_backoff_base

    for attempt in range(retries):
        try:
            if role == LlmRole.COFOUNDER:
                client = _getCerebrasClient()
                response = await client.chat.completions.create(
                    model=settings.cerebras_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=maxTokens,
                )
            elif role == LlmRole.ARCHITECT:
                client = _getOpenaiClient()
                response = await client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=maxTokens,
                )
            elif role == LlmRole.EXECUTOR:
                client = _getSiliconflowClient()
                response = await client.chat.completions.create(
                    model=settings.siliconflow_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=maxTokens,
                )
            else:
                raise ValueError(f"Unknown LLM role: {role}")

            return response.choices[0].message.content or ""

        except Exception as e:
            errStr = str(e)
            if "429" in errStr and attempt < retries - 1:
                logger.warning(
                    f"Rate limited ({role.value}), backing off {backoff:.1f}s "
                    f"(attempt {attempt + 1}/{retries})"
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, settings.siliconflow_backoff_max)
            else:
                logger.error(f"LLM call failed ({role.value}): {e}")
                raise


# ── Streaming Chat Completion ──────────────────────────────────

async def chatCompletionStream(
    role: LlmRole,
    messages: list[dict],
    temperature: float = 0.7,
    maxTokens: int = 4096,
) -> AsyncGenerator[str, None]:
    """
    Streaming chat completion. Yields content deltas as they arrive.
    """
    if role == LlmRole.COFOUNDER:
        client = _getCerebrasClient()
        stream = await client.chat.completions.create(
            model=settings.cerebras_model,
            messages=messages,
            temperature=temperature,
            max_tokens=maxTokens,
            stream=True,
        )
    elif role == LlmRole.ARCHITECT:
        client = _getOpenaiClient()
        stream = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=maxTokens,
            stream=True,
        )
    elif role == LlmRole.EXECUTOR:
        client = _getSiliconflowClient()
        stream = await client.chat.completions.create(
            model=settings.siliconflow_model,
            messages=messages,
            temperature=temperature,
            max_tokens=maxTokens,
            stream=True,
        )
    else:
        raise ValueError(f"Unknown LLM role: {role}")

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
