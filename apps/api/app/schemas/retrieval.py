from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class RetrievalDebugRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    chunk_index: int
    page_number: int | None
    score: float
    text: str


class RetrievalDebugResponse(BaseModel):
    query: str
    top_k: int
    results: list[RetrievedChunk]
