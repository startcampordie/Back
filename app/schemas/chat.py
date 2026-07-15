from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ChatIntent(str, Enum):
    ATTRACTION = "attraction"
    CULTURE = "culture"
    RESTAURANT = "restaurant"
    FESTIVAL = "festival"


class ChatRequest(BaseModel):
    session_id: str
    intent: ChatIntent

    message: str = Field(
        min_length=2,
        max_length=100,
        examples=["북구 관광지 추천해줘"],
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("질문을 입력해 주세요.")

        return value


class ChatReference(BaseModel):
    type: str
    id: int
    title: str

    category: str | None = None
    address: str | None = None
    telephone: str | None = None
    view_count: int | None = None


class ChatResponse(BaseModel):
    session_id: str
    intent: ChatIntent
    answer: str
    total: int
    references: list[ChatReference]
    created_at: datetime


class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    intent: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]