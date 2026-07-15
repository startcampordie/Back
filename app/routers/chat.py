from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat_message import ChatMessage
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
)
from app.services.chat_service import (
    create_chat_session,
    get_chat_session,
    is_session_expired,
    process_chat,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=201,
)
def create_session(
    db: Session = Depends(get_db),
):
    return create_chat_session(db)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ChatHistoryResponse,
)
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
):
    session = get_chat_session(
        db=db,
        session_id=session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="채팅 세션을 찾을 수 없습니다.",
        )

    if is_session_expired(session):
        raise HTTPException(
            status_code=410,
            detail="만료된 채팅 세션입니다.",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return {
        "session_id": session_id,
        "messages": messages,
    }


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    session = get_chat_session(
        db=db,
        session_id=request.session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="채팅 세션을 찾을 수 없습니다.",
        )

    if is_session_expired(session):
        raise HTTPException(
            status_code=410,
            detail="만료된 채팅 세션입니다.",
        )

    return process_chat(
        db=db,
        session=session,
        user_message=request.message,
    )