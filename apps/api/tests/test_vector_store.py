import uuid

import httpx
import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.vector_store import QdrantVectorStore


def test_qdrant_upsert_rejects_embedding_count_mismatch() -> None:
    document = Document(id=uuid.uuid4(), original_filename="source.txt")
    chunk = Chunk(id=uuid.uuid4(), document_id=document.id, chunk_index=0, text="hello")
    store = QdrantVectorStore("http://qdrant:6333", "rag_chunks", 768)

    with pytest.raises(ValueError, match="Chunk and embedding counts do not match"):
        store.upsert_chunks(document, [chunk], [])


def test_qdrant_upsert_writes_chunk_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    requests = []

    def fake_put(url, **kwargs):
        requests.append({"url": url, "json": kwargs["json"]})
        return httpx.Response(200, request=httpx.Request("PUT", url), json={"status": "ok"})

    monkeypatch.setattr(httpx, "put", fake_put)

    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    document = Document(id=document_id, original_filename="source.txt")
    chunk = Chunk(
        id=chunk_id,
        document_id=document_id,
        chunk_index=2,
        page_number=7,
        text="grounded context",
    )
    store = QdrantVectorStore("http://qdrant:6333", "rag_chunks", 3)

    store.upsert_chunks(document, [chunk], [[0.1, 0.2, 0.3]])

    point = requests[0]["json"]["points"][0]
    assert requests[0]["url"] == "http://qdrant:6333/collections/rag_chunks/points?wait=true"
    assert point["id"] == str(chunk_id)
    assert point["vector"] == [0.1, 0.2, 0.3]
    assert point["payload"] == {
        "chunk_id": str(chunk_id),
        "document_id": str(document_id),
        "filename": "source.txt",
        "chunk_index": 2,
        "page_number": 7,
        "text": "grounded context",
    }
