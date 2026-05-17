from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.chat import ChatSession
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate, ChatSessionRead, ChatTurnResponse
from app.services.rag import answer_question

router = APIRouter(prefix="/chat/sessions", tags=["chat"])


@router.post("", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    request: ChatSessionCreate,
    db: Session = Depends(get_db),
) -> ChatSession:
    session = ChatSession(title=request.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=ChatSessionRead)
def get_chat_session(session_id: uuid.UUID, db: Session = Depends(get_db)) -> ChatSession:
    session = db.scalar(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    return session


@router.post("/{session_id}/messages", response_model=ChatTurnResponse)
def create_chat_message(
    session_id: uuid.UUID,
    request: ChatMessageCreate,
    db: Session = Depends(get_db),
) -> ChatTurnResponse:
    session = db.get(ChatSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")

    user_message, assistant_message = answer_question(
        db, session, request.content, top_k=request.top_k
    )
    return ChatTurnResponse(user_message=user_message, assistant_message=assistant_message)
