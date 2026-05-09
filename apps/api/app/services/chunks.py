from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.chunking import TextChunk, chunk_text


def replace_document_chunks(db: Session, document: Document, text: str) -> list[Chunk]:
    db.execute(delete(Chunk).where(Chunk.document_id == document.id))
    text_chunks = chunk_text(text)
    chunks = [
        Chunk(
            document_id=document.id,
            chunk_index=item.chunk_index,
            text=item.text,
            token_count=item.token_count,
            char_start=item.char_start,
            char_end=item.char_end,
            page_number=item.page_number,
            chunk_metadata={
                "strategy": "fixed_token_window",
                "chunk_tokens": 800,
                "overlap_tokens": 150,
            },
        )
        for item in text_chunks
    ]
    db.add_all(chunks)
    return chunks
