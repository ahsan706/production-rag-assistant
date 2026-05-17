from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import Citation
from app.schemas.retrieval import RetrievedChunk
from app.services.chat_provider import ChatProvider, get_chat_provider
from app.services.retrieval import retrieve_relevant_chunks

SYSTEM_PROMPT = """You are a grounded RAG assistant.
Use only the provided context to answer.
If the context does not support the answer, say: I don't know based on the provided documents.
Cite every factual sentence with bracketed citation labels like [1].
Do not cite sources that are not in the context.
Keep answers concise and direct."""


def answer_question(
    db: Session,
    session: ChatSession,
    question: str,
    top_k: int = 5,
    chat_provider: ChatProvider | None = None,
) -> tuple[ChatMessage, ChatMessage]:
    retrieved = retrieve_relevant_chunks(db, question, top_k=top_k)
    supported_chunks = [chunk for chunk in retrieved if chunk.score >= settings.retrieval_min_score]

    user_message = ChatMessage(session_id=session.id, role="user", content=question)
    db.add(user_message)
    db.flush()

    if not supported_chunks:
        answer = "I don't know based on the provided documents."
        citations: list[Citation] = []
        metadata = {"unsupported": True, "reason": "retrieval_score_below_threshold"}
    else:
        citations = build_citations(supported_chunks)
        context = build_context(supported_chunks)
        provider = chat_provider or get_chat_provider()
        answer = provider.generate(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer with citations."
                    ),
                },
            ],
            temperature=0.0,
        )
        metadata = {"unsupported": False}
        if _is_refusal(answer):
            citations = []
            metadata = {"unsupported": True, "reason": "model_refusal"}
        elif not _contains_citation(answer):
            answer = f"{answer} [{citations[0].label}]"

    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
        citations=[citation.model_dump(mode="json") for citation in citations],
        retrieved_context=[chunk.model_dump(mode="json") for chunk in retrieved],
        message_metadata=metadata,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(user_message)
    db.refresh(assistant_message)
    return user_message, assistant_message


def build_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for label, chunk in enumerate(chunks, start=1):
        location = f"{chunk.filename}, chunk {chunk.chunk_index}"
        if chunk.page_number is not None:
            location += f", page {chunk.page_number}"
        blocks.append(f"[{label}] {location}\n{chunk.text}")
    return "\n\n".join(blocks)


def build_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            label=index,
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            filename=chunk.filename,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            score=chunk.score,
            excerpt=chunk.text[:500],
        )
        for index, chunk in enumerate(chunks, start=1)
    ]


def _contains_citation(answer: str) -> bool:
    return any(f"[{number}]" in answer for number in range(1, 21))


def _is_refusal(answer: str) -> bool:
    return answer.strip().lower().startswith("i don't know based on the provided documents")
