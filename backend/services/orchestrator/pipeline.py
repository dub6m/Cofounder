"""
Main orchestration pipeline — the state machine that drives the entire
Design-First, Code-Second flow.

Phase A: Technical Lead Cofounder (negotiation → architecture)
Phase B: Sandboxed Execution (architecture → execution)  [Phase 3]
Phase C: Feedback Loop (execution → evaluation)           [Phase 4]
Phase D: Deployment (evaluation → deployment)              [Phase 4]

This module implements Phase A for Phase 1 of the MVP.
The LLM now uses a "Pitch & Refine" conversational flow —
no Decision Cards, just natural markdown responses.
"""

import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.websocket.handler import manager
from core.models import ArchitectureSnapshot, Conversation, Message
from schemas.ws_events import EventType
from services.llm.router import LlmRole, chatCompletion

logger = logging.getLogger(__name__)

# Load system prompts
_promptDir = Path(__file__).parent.parent / "llm" / "prompts"
COFOUNDER_SYSTEM_PROMPT = (_promptDir / "cofounder_system.txt").read_text(encoding="utf-8")
ARCHITECT_SYSTEM_PROMPT = (_promptDir / "architect_system.txt").read_text(encoding="utf-8")


# ── Finalize Detector ──────────────────────────────────────────

def detectFinalize(content: str) -> bool:
    """Check if the LLM wants to finalize the architecture."""
    triggers = [
        "finalize_architecture",
        "all constraints are locked",
        "generate the architecture diagrams",
        "I will now generate the architecture",
    ]
    lowerContent = content.lower()
    return any(t.lower() in lowerContent for t in triggers)


# ── Conversation History Builder ───────────────────────────────

async def buildMessageHistory(
    session: AsyncSession,
    conversationId: str,
) -> list[dict]:
    """
    Load all messages for a conversation and format them for the LLM.
    """
    result = await session.execute(
        select(Message)
        .where(Message.conversationId == conversationId)
        .order_by(Message.createdAt)
    )
    messages = result.scalars().all()

    history = [{"role": "system", "content": COFOUNDER_SYSTEM_PROMPT}]
    for msg in messages:
        role = msg.role
        if role in ("user", "assistant", "system"):
            history.append({"role": role, "content": msg.content})

    return history


# ── Main Chat Handler ──────────────────────────────────────────

async def handleUserMessage(
    session: AsyncSession,
    conversationId: str,
    userContent: str,
    clientId: str = "default",
) -> str:
    """
    Process a user message through the Technical Lead pipeline.
    1. Save user message to DB
    2. Build chat history
    3. Call the Cofounder LLM
    4. Detect finalize trigger
    5. Save assistant message to DB
    6. Emit WS events
    """
    # 1. Save user message
    userMsg = Message(
        conversationId=conversationId,
        role="user",
        content=userContent,
    )
    session.add(userMsg)
    await session.flush()

    # 2. Build history
    history = await buildMessageHistory(session, conversationId)

    # 3. Call Cofounder LLM
    assistantContent = await chatCompletion(
        role=LlmRole.COFOUNDER,
        messages=history,
        temperature=0.7,
        maxTokens=4096,
    )

    # 4. Check for finalize trigger
    shouldFinalize = detectFinalize(assistantContent)

    # 5. Save assistant message
    assistantMsg = Message(
        conversationId=conversationId,
        role="assistant",
        content=assistantContent,
    )
    session.add(assistantMsg)

    # 6. Emit events — send the raw markdown content to the frontend
    await manager.sendEvent(
        EventType.CHAT_MESSAGE,
        {
            "role": "assistant",
            "content": assistantContent,
        },
        clientId=clientId,
    )

    # Handle finalize
    if shouldFinalize:
        conversation = await session.get(Conversation, conversationId)
        if conversation:
            conversation.phase = "architecture"

        await manager.sendEvent(
            EventType.PHASE_CHANGE,
            {"from_phase": "negotiation", "to_phase": "architecture"},
            clientId=clientId,
        )

        # Trigger Mermaid generation (Phase 2 implementation)
        logger.info(f"Architecture finalization triggered for {conversationId}")

    await session.commit()
    return assistantContent
