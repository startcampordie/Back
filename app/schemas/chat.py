from datetime import datetime

from pydantic import BaseModel, Field


class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(
        min_length=1,
        max_length=500,
        examples=["북구에 있는 관광지 추천해줘"],
    )


class ChatReference(BaseModel):
    type: str
    id: int
    title: str
    category: str | None = None
    address: str | None = None
    telephone: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    answer: str
    references: list[ChatReference]
    created_at: datetime


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