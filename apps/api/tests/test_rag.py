import uuid

from app.schemas.retrieval import RetrievedChunk
from app.services.rag import _is_refusal, build_citations, build_context


def _chunk(index: int, score: float = 0.81) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename="source.md",
        chunk_index=index,
        page_number=None,
        score=score,
        text=f"Grounded fact {index}.",
    )


def test_build_context_numbers_retrieved_chunks() -> None:
    context = build_context([_chunk(0), _chunk(1)])

    assert "[1] source.md, chunk 0" in context
    assert "[2] source.md, chunk 1" in context
    assert "Grounded fact 0." in context


def test_build_citations_preserves_source_metadata() -> None:
    chunk = _chunk(3, score=0.72)

    citation = build_citations([chunk])[0]

    assert citation.label == 1
    assert citation.chunk_id == chunk.chunk_id
    assert citation.document_id == chunk.document_id
    assert citation.filename == "source.md"
    assert citation.chunk_index == 3
    assert citation.score == 0.72


def test_is_refusal_detects_grounding_refusal() -> None:
    assert _is_refusal("I don't know based on the provided documents.")
    assert not _is_refusal("The answer is Qdrant. [1]")
