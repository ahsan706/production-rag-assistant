from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.retrieval import RetrievedChunk
from app.services.embeddings import EmbeddingProvider, get_embedding_provider
from app.services.vector_store import QdrantVectorStore, get_vector_store


def retrieve_relevant_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    embedding_provider: EmbeddingProvider | None = None,
    vector_store: QdrantVectorStore | None = None,
) -> list[RetrievedChunk]:
    provider = embedding_provider or get_embedding_provider()
    store = vector_store or get_vector_store()

    query_vector = provider.embed_texts([query])[0]
    raw_results = store.search(query_vector, limit=top_k)
    sorted_results = sorted(raw_results, key=lambda result: result.get("score", 0.0), reverse=True)

    chunk_ids = [_extract_chunk_id(result) for result in sorted_results]
    chunk_ids = [chunk_id for chunk_id in chunk_ids if chunk_id is not None]
    if not chunk_ids:
        return []

    rows = db.execute(
        select(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.id.in_(chunk_ids))
    ).all()
    chunks_by_id = {chunk.id: (chunk, document) for chunk, document in rows}

    hydrated: list[RetrievedChunk] = []
    for result in sorted_results:
        chunk_id = _extract_chunk_id(result)
        if chunk_id is None or chunk_id not in chunks_by_id:
            continue

        chunk, document = chunks_by_id[chunk_id]
        hydrated.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=document.id,
                filename=document.original_filename,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                score=float(result.get("score", 0.0)),
                text=chunk.text,
            )
        )

    return hydrated


def _extract_chunk_id(result: dict) -> uuid.UUID | None:
    payload = result.get("payload") or {}
    raw_id = payload.get("chunk_id") or result.get("id")
    if raw_id is None:
        return None
    try:
        return uuid.UUID(str(raw_id))
    except ValueError:
        return None
