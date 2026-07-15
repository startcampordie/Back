from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# 게시글 작성 요청
class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    password: str = Field(min_length=4, max_length=100)

    @field_validator("title", "content")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value



# 게시글 수정 요청
class PostUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    password: str = Field(min_length=4, max_length=100)

    @field_validator("title", "content")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


# 수정 및 삭제 비밀번호 확인 요청
class PostPasswordRequest(BaseModel):
    password: str = Field(min_length=4, max_length=100)


# 비밀번호 확인 응답
class PasswordVerifyResponse(BaseModel):
    verified: bool


# 공통 메시지 응답
class MessageResponse(BaseModel):
    message: str



# 게시글 응답
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    view_count: int
    created_at: datetime
    updated_at: datetime


    class Config:
        from_attributes = True


# 게시글 목록 항목 응답
class PostListItem(BaseModel):
    id: int
    title: str
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# 게시글 목록 및 페이지 정보 응답
class PostListResponse(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    items: list[PostListItem]
