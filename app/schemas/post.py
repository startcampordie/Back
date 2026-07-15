from datetime import datetime

from pydantic import BaseModel


# 게시글 작성 요청
class PostCreate(BaseModel):
    title: str
    content: str
    password: str



# 게시글 수정 요청
class PostUpdate(BaseModel):
    title: str
    content: str
    password: str



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
