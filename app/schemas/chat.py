from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ChatIntent(str, Enum):
    ATTRACTION = "attraction"
    CULTURE = "culture"
    RESTAURANT = "restaurant"
    FESTIVAL = "festival"


class ChatRequest(BaseModel):
    session_id: str = Field(
        description=(
            "POST /api/chat/sessions에서 발급받은 "
            "채팅 세션 UUID"
        ),
        examples=[
            "550e8400-e29b-41d4-a716-446655440000"
        ],
    )

    intent: ChatIntent = Field(
        description=(
            "검색 유형. "
            "attraction=관광지, "
            "culture=문화시설, "
            "restaurant=음식점, "
            "festival=축제·행사"
        ),
        examples=["restaurant"],
    )

    message: str = Field(
        min_length=2,
        max_length=100,
        description=(
            "사용자 질문. 지역명을 포함하면 "
            "해당 시·군·구로 검색합니다."
        ),
        examples=["북구 맛집 알려줘"],
    )

    @field_validator("message")
    @classmethod
    def validate_message(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "질문을 입력해 주세요."
            )

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": (
                    "550e8400-e29b-41d4-"
                    "a716-446655440000"
                ),
                "intent": "restaurant",
                "message": "북구 맛집 알려줘",
            }
        }
    )


class ChatReference(BaseModel):
    type: str = Field(
        description="검색 결과 유형",
        examples=["regional_content"],
    )

    id: int = Field(
        description="지역 정보 또는 게시글 ID",
        examples=[15],
    )

    title: str = Field(
        description="장소 또는 게시글 제목",
        examples=["제일반점"],
    )

    category: str | None = Field(
        default=None,
        description="지역 정보 카테고리",
        examples=["RESTAURANT"],
    )

    address: str | None = Field(
        default=None,
        description="장소 주소",
        examples=[
            "광주광역시 북구 서방로 24"
        ],
    )

    telephone: str | None = Field(
        default=None,
        description="장소 전화번호",
        examples=["062-123-4567"],
    )

    image_url: str | None = Field(
        default=None,
        description="장소 대표 이미지 URL",
    )

    image_thumbnail_url: str | None = Field(
        default=None,
        description="장소 썸네일 이미지 URL",
    )

    reason: str | None = Field(
        default=None,
        description=(
            "AI가 해당 검색 결과를 선택한 이유. "
            "OpenAI 실패 시 null"
        ),
        examples=[
            "북구 음식점을 찾는 질문 조건과 일치합니다."
        ],
    )

    view_count: int | None = Field(
        default=None,
        description=(
            "게시글 조회수. "
            "지역 정보인 경우 null"
        ),
        examples=[24],
    )


class ChatResponse(BaseModel):
    session_id: str = Field(
        description="채팅 세션 UUID",
    )

    intent: ChatIntent = Field(
        description="처리된 검색 유형",
    )

    answer: str = Field(
        description=(
            "검색 결과에 대한 전체 안내 문장. "
            "각 장소의 설명은 references의 "
            "reason에서 확인합니다."
        ),
        examples=[
            "북구에서 조건에 맞는 음식점을 안내해 드릴게요."
        ],
    )

    total: int = Field(
        description=(
            "DB에서 조건에 맞는 전체 결과 수"
        ),
        examples=[23],
    )

    references: list[ChatReference] = Field(
        description=(
            "AI가 선택한 검색 결과와 선택 이유. "
            "최대 5건. OpenAI 실패 시 서버 검색 "
            "결과 최대 5건을 반환합니다."
        ),
    )

    created_at: datetime = Field(
        description="챗봇 답변 생성 시각",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": (
                    "550e8400-e29b-41d4-"
                    "a716-446655440000"
                ),
                "intent": "restaurant",
                "answer": (
                    "북구에서 조건에 맞는 음식점을 "
                    "안내해 드릴게요."
                ),
                "total": 23,
                "references": [
                    {
                        "type": (
                            "regional_content"
                        ),
                        "id": 15,
                        "title": "제일반점",
                        "category": "RESTAURANT",
                        "address": (
                            "광주광역시 북구 "
                            "서방로 24"
                        ),
                        "telephone": (
                            "062-123-4567"
                        ),
                        "image_url": (
                            "https://example.com/"
                            "image.jpg"
                        ),
                        "image_thumbnail_url": (
                            "https://example.com/"
                            "thumbnail.jpg"
                        ),
                        "reason": (
                            "북구 음식점을 찾는 질문 "
                            "조건과 일치합니다."
                        ),
                        "view_count": None,
                    }
                ],
                "created_at": (
                    "2026-07-15T15:30:00"
                ),
            }
        }
    )


class ChatSessionResponse(BaseModel):
    session_id: str = Field(
        description="새로 발급된 세션 UUID",
    )

    created_at: datetime = Field(
        description="세션 생성 시각",
    )

    expires_at: datetime = Field(
        description=(
            "세션 만료 시각. "
            "마지막 이용 후 7일"
        ),
    )

    model_config = ConfigDict(
        from_attributes=True
    )


class ChatMessageResponse(BaseModel):
    id: int
    role: str = Field(
        description="user 또는 assistant",
        examples=["user"],
    )
    content: str = Field(
        description="질문 또는 답변 내용",
    )
    intent: str | None = Field(
        description="메시지의 검색 유형",
    )
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]