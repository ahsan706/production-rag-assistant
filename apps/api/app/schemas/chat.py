from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)


class Citation(BaseModel):
    label: int
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    chunk_index: int
    page_number: int | None
    score: float
    excerpt: str


class ChatMessageRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    status: str
    error_message: str | None
    citations: list[dict[str, Any]]
    retrieved_context: list[dict[str, Any]]
    message_metadata: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionRead(BaseModel):
    id: uuid.UUID
    title: str | None
    status: str
    error_message: str | None
    session_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageRead] = []

    model_config = ConfigDict(from_attributes=True)


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatTurnResponse(BaseModel):
    user_message: ChatMessageRead
    assistant_message: ChatMessageRead
