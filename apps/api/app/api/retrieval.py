from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.retrieval import RetrievalDebugRequest, RetrievalDebugResponse
from app.services.retrieval import retrieve_relevant_chunks

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/debug", response_model=RetrievalDebugResponse)
def debug_retrieval(
    request: RetrievalDebugRequest,
    db: Session = Depends(get_db),
) -> RetrievalDebugResponse:
    results = retrieve_relevant_chunks(db, request.query, top_k=request.top_k)
    return RetrievalDebugResponse(query=request.query, top_k=request.top_k, results=results)
