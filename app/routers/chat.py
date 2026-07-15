from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)
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
    status_code=status.HTTP_201_CREATED,
    summary="채팅 세션 생성",
    description=(
        "로그인 없이 사용할 수 있는 채팅 세션을 생성합니다. "
        "반환된 session_id를 질문 요청에 사용합니다. "
        "세션은 마지막 이용 후 7일 동안 유효합니다."
    ),
    response_description=(
        "생성된 세션 UUID와 만료 시각"
    ),
    responses={
        201: {
            "description": (
                "채팅 세션 생성 성공"
            )
        },
        500: {
            "description": (
                "서버 또는 데이터베이스 오류"
            )
        },
    },
)
def create_session(
    db: Session = Depends(get_db),
):
    return create_chat_session(db)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ChatHistoryResponse,
    summary="채팅 히스토리 조회",
    description=(
        "세션 UUID를 이용해 사용자 질문과 "
        "챗봇 답변을 시간순으로 조회합니다."
    ),
    response_description=(
        "해당 세션에 저장된 전체 메시지"
    ),
    responses={
        200: {
            "description": (
                "채팅 히스토리 조회 성공"
            )
        },
        404: {
            "description": (
                "채팅 세션을 찾을 수 없음"
            )
        },
        410: {
            "description": (
                "채팅 세션이 만료됨"
            )
        },
    },
)
def get_chat_history(
    session_id: str = Path(
        ...,
        description=(
            "POST /api/chat/sessions에서 "
            "발급받은 세션 UUID"
        ),
        examples=[
            "550e8400-e29b-41d4-"
            "a716-446655440000"
        ],
    ),
    db: Session = Depends(get_db),
):
    session = get_chat_session(
        db=db,
        session_id=session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail=(
                "채팅 세션을 찾을 수 없습니다."
            ),
        )

    if is_session_expired(session):
        raise HTTPException(
            status_code=410,
            detail="만료된 채팅 세션입니다.",
        )

    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id
            == session_id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .all()
    )

    return {
        "session_id": session_id,
        "messages": messages,
    }


@router.post(
    "",
    response_model=ChatResponse,
    summary="챗봇 질문 전송",
    description="""
사용자가 선택한 검색 유형과 질문으로 지역 정보를 검색합니다.

- `attraction`: 관광지
- `culture`: 문화시설
- `restaurant`: 음식점
- `festival`: 축제·행사

서버가 DB에서 최대 10건의 후보를 검색한 후 OpenAI가
최대 5건을 선택합니다.

응답의 `answer`에는 전체 안내 문장이 들어갑니다.
`references`에는 AI가 선택한 장소의 ID, 이름, 주소,
이미지 URL과 선택 이유인 `reason`이 들어갑니다.

OpenAI가 반환한 ID가 서버 검색 결과에 존재하는지 검증하며,
존재하지 않는 ID는 응답에서 제외합니다.

OpenAI 호출이 실패하면 서버 검색 결과 최대 5건을 반환하고
`references[].reason`은 null로 반환합니다.
""",
    response_description=(
        "전체 안내 문장과 AI가 선택한 "
        "최대 5건의 검색 결과"
    ),
    responses={
        200: {
            "description": (
                "질문 처리 성공. 검색 결과가 "
                "없어도 200을 반환합니다."
            )
        },
        404: {
            "description": (
                "채팅 세션을 찾을 수 없음"
            )
        },
        410: {
            "description": (
                "마지막 이용 후 7일이 지나 "
                "채팅 세션이 만료됨"
            )
        },
        422: {
            "description": (
                "intent가 잘못됐거나 질문이 "
                "2~100자 범위를 벗어남"
            )
        },
    },
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
            detail=(
                "채팅 세션을 찾을 수 없습니다."
            ),
        )

    if is_session_expired(session):
        raise HTTPException(
            status_code=410,
            detail="만료된 채팅 세션입니다.",
        )

    return process_chat(
        db=db,
        session=session,
        intent=request.intent.value,
        message=request.message,
    )