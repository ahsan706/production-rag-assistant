from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.models.chunk import Chunk
from app.models.document import Document


class QdrantVectorStore:
    def __init__(self, url: str, collection: str, vector_size: int) -> None:
        self.url = url.rstrip("/")
        self.collection = collection
        self.vector_size = vector_size

    def ensure_collection(self) -> None:
        response = httpx.get(
            f"{self.url}/collections/{self.collection}",
            timeout=settings.qdrant_request_timeout_seconds,
        )
        if response.status_code == 200:
            return
        if response.status_code != 404:
            response.raise_for_status()

        create_response = httpx.put(
            f"{self.url}/collections/{self.collection}",
            json={"vectors": {"size": self.vector_size, "distance": "Cosine"}},
            timeout=settings.qdrant_request_timeout_seconds,
        )
        create_response.raise_for_status()

    def upsert_chunks(
        self,
        document: Document,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunk and embedding counts do not match.")

        points: list[dict[str, Any]] = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                {
                    "id": str(chunk.id),
                    "vector": embedding,
                    "payload": {
                        "chunk_id": str(chunk.id),
                        "document_id": str(document.id),
                        "filename": document.original_filename,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "text": chunk.text,
                    },
                }
            )

        response = httpx.put(
            f"{self.url}/collections/{self.collection}/points?wait=true",
            json={"points": points},
            timeout=settings.qdrant_request_timeout_seconds,
        )
        response.raise_for_status()

    def search(self, vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        response = httpx.post(
            f"{self.url}/collections/{self.collection}/points/search",
            json={"vector": vector, "limit": limit, "with_payload": True},
            timeout=settings.qdrant_request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()["result"]


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore(
        url=settings.qdrant_url,
        collection=settings.qdrant_collection,
        vector_size=settings.ai_embedding_dimensions,
    )
