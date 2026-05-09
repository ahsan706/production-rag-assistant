import uuid

from app.services.retrieval import _extract_chunk_id, retrieve_relevant_chunks


class FakeEmbeddingProvider:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["nothing relevant"]
        return [[0.1, 0.2, 0.3]]


class EmptyVectorStore:
    def search(self, vector: list[float], limit: int = 5) -> list[dict]:
        assert vector == [0.1, 0.2, 0.3]
        assert limit == 3
        return []


class NoQuerySession:
    def execute(self, *args, **kwargs):
        raise AssertionError("database should not be queried when vector search returns no results")


def test_retrieve_relevant_chunks_returns_empty_results_without_db_query() -> None:
    assert (
        retrieve_relevant_chunks(
            NoQuerySession(),
            "nothing relevant",
            top_k=3,
            embedding_provider=FakeEmbeddingProvider(),
            vector_store=EmptyVectorStore(),
        )
        == []
    )


def test_extract_chunk_id_prefers_payload_chunk_id() -> None:
    chunk_id = uuid.uuid4()
    result_id = uuid.uuid4()

    assert _extract_chunk_id({"id": str(result_id), "payload": {"chunk_id": str(chunk_id)}}) == chunk_id


def test_extract_chunk_id_falls_back_to_result_id() -> None:
    chunk_id = uuid.uuid4()

    assert _extract_chunk_id({"id": str(chunk_id), "payload": {}}) == chunk_id


def test_extract_chunk_id_ignores_invalid_ids() -> None:
    assert _extract_chunk_id({"id": "not-a-uuid", "payload": {}}) is None
