"""
Main orchestration pipeline — the state machine that drives the entire
Design-First, Code-Second flow.

Phase A: Inquisitive Cofounder (negotiation → architecture)
Phase B: Sandboxed Execution (architecture → execution)  [Phase 3]
Phase C: Feedback Loop (execution → evaluation)           [Phase 4]
Phase D: Deployment (evaluation → deployment)              [Phase 4]

This module implements Phase A for Phase 1 of the MVP.
"""

import logging
import re
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.websocket.handler import manager
from core.models import ArchitectureSnapshot, Conversation, Message
from schemas.ws_events import EventType
from services.llm.router import LlmRole, chatCompletion, chatCompletionStream

logger = logging.getLogger(__name__)

# Load system prompts
_promptDir = Path(__file__).parent.parent / "llm" / "prompts"
COFOUNDER_SYSTEM_PROMPT = (_promptDir / "cofounder_system.txt").read_text(encoding="utf-8")
ARCHITECT_SYSTEM_PROMPT = (_promptDir / "architect_system.txt").read_text(encoding="utf-8")


# ── Decision Card Parser ───────────────────────────────────────

DECISION_PATTERN = re.compile(
    r"###\s*🎯\s*Decision Required:\s*\n"
    r"\*\*(.+?)\*\*\s*\n\n"                   # question
    r"\*\*Option A:\s*(.+?)\*\*\s*\n"          # option A label
    r"(.+?)\n\n"                                # option A description
    r"\*\*Option B:\s*(.+?)\*\*\s*\n"          # option B label
    r"(.+?)(?:\n\n|\Z)",                        # option B description
    re.DOTALL,
)


def parseDecisionCards(content: str) -> list[dict]:
    """
    Extract Decision Card data from LLM Markdown output.
    Returns a list of decision dicts ready for the frontend.
    """
    decisions = []
    for match in DECISION_PATTERN.finditer(content):
        decisions.append({
            "id": str(uuid.uuid4()),
            "question": match.group(1).strip(),
            "options": [
                {
                    "label": match.group(2).strip(),
                    "value": "option_a",
                    "description": match.group(3).strip(),
                },
                {
                    "label": match.group(4).strip(),
                    "value": "option_b",
                    "description": match.group(5).strip(),
                },
            ],
        })
    return decisions


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
    'hidden' role messages are sent as 'user' to maintain context.
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
        if role == "hidden":
            role = "user"
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
    Process a user message through the Inquisitive Cofounder pipeline.
    1. Save user message to DB
    2. Build chat history
    3. Call the Cofounder LLM (streaming)
    4. Parse response for Decision Cards
    5. Detect finalize trigger
    6. Save assistant message to DB
    7. Emit WS events
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

    # 3. Call Cofounder LLM (non-streaming for reliability in Phase 1)
    assistantContent = await chatCompletion(
        role=LlmRole.COFOUNDER,
        messages=history,
        temperature=0.7,
        maxTokens=4096,
    )

    # 4. Parse Decision Cards
    decisions = parseDecisionCards(assistantContent)

    # 5. Check for finalize trigger
    shouldFinalize = detectFinalize(assistantContent)

    # 6. Save assistant message
    assistantMsg = Message(
        conversationId=conversationId,
        role="assistant",
        content=assistantContent,
        metadata_={"decisions": decisions} if decisions else None,
    )
    session.add(assistantMsg)

    # 7. Emit events
    # Always emit the chat message
    await manager.sendEvent(
        EventType.CHAT_MESSAGE,
        {
            "role": "assistant",
            "content": assistantContent,
            "metadata": {"decisions": decisions} if decisions else None,
        },
        clientId=clientId,
    )

    # Emit individual Decision Required events
    for decision in decisions:
        await manager.sendEvent(
            EventType.DECISION_REQUIRED,
            decision,
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


# ── Decision Response Handler ──────────────────────────────────

async def handleDecisionResponse(
    session: AsyncSession,
    conversationId: str,
    decisionId: str,
    selectedValue: str,
    clientId: str = "default",
) -> str:
    """
    Handle a user's decision card selection.
    Injects the choice as a hidden message and continues the conversation.
    """
    # Find the decision in recent messages
    result = await session.execute(
        select(Message)
        .where(Message.conversationId == conversationId)
        .where(Message.role == "assistant")
        .order_by(Message.createdAt.desc())
        .limit(5)
    )
    recentMessages = result.scalars().all()

    # Find the decision data
    selectedLabel = selectedValue
    for msg in recentMessages:
        if msg.metadata_ and "decisions" in msg.metadata_:
            for d in msg.metadata_["decisions"]:
                if d["id"] == decisionId:
                    for opt in d["options"]:
                        if opt["value"] == selectedValue:
                            selectedLabel = opt["label"]
                    break

    # Inject as hidden message
    hiddenContent = f"I choose: {selectedLabel}"
    hiddenMsg = Message(
        conversationId=conversationId,
        role="hidden",
        content=hiddenContent,
        metadata_={"decision_id": decisionId, "selected_value": selectedValue},
    )
    session.add(hiddenMsg)
    await session.flush()

    # Continue the conversation
    return await handleUserMessage(
        session, conversationId, hiddenContent, clientId
    )
