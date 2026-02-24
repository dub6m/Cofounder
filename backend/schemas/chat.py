"""
Pydantic models for chat-related REST and internal schemas.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    conversationId: str = Field(..., alias="conversation_id")
    role: str
    content: str
    metadata: Optional[dict[str, Any]] = None
    createdAt: datetime = Field(..., alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    phase: str
    createdAt: datetime = Field(..., alias="created_at")
    updatedAt: datetime = Field(..., alias="updated_at")

    class Config:
        from_attributes = True
        populate_by_name = True


class ConversationWithMessages(ConversationResponse):
    messages: list[MessageResponse] = []
