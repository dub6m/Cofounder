"""
REST API routes for chat operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import getSession
from core.models import Conversation, Message
from schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse)
async def createConversation(
    data: ConversationCreate,
    session: AsyncSession = Depends(getSession),
):
    """Create a new conversation."""
    conversation = Conversation(title=data.title)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        phase=conversation.phase,
        created_at=conversation.createdAt,
        updated_at=conversation.updatedAt,
    )


@router.get("/", response_model=list[ConversationResponse])
async def listConversations(
    session: AsyncSession = Depends(getSession),
):
    """List all conversations, most recent first."""
    result = await session.execute(
        select(Conversation).order_by(Conversation.createdAt.desc())
    )
    conversations = result.scalars().all()
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            phase=c.phase,
            created_at=c.createdAt,
            updated_at=c.updatedAt,
        )
        for c in conversations
    ]


@router.get("/{conversationId}", response_model=ConversationWithMessages)
async def getConversation(
    conversationId: str,
    session: AsyncSession = Depends(getSession),
):
    """Get a conversation with all its messages."""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.id == conversationId)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationWithMessages(
        id=conversation.id,
        title=conversation.title,
        phase=conversation.phase,
        created_at=conversation.createdAt,
        updated_at=conversation.updatedAt,
        messages=[
            MessageResponse(
                id=m.id,
                conversation_id=m.conversationId,
                role=m.role,
                content=m.content,
                metadata=m.metadata_,
                created_at=m.createdAt,
            )
            for m in conversation.messages
            if m.role != "hidden"  # Don't expose hidden messages
        ],
    )


@router.delete("/{conversationId}")
async def deleteConversation(
    conversationId: str,
    session: AsyncSession = Depends(getSession),
):
    """Delete a conversation and all associated data."""
    conversation = await session.get(Conversation, conversationId)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await session.delete(conversation)
    await session.commit()
    return {"status": "deleted"}
