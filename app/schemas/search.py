from datetime import datetime

from pydantic import BaseModel


class SearchContentItem(BaseModel):
    id: int
    category: str
    tag: str | None
    title: str
    address: str | None
    image_url: str | None

    class Config:
        from_attributes = True


class SearchPostItem(BaseModel):
    id: int
    title: str
    content_preview: str
    created_at: datetime
    view_count: int


class SearchResponse(BaseModel):
    keyword: str
    search_type: str
    district: str | None
    total_count: int

    attractions: list[SearchContentItem]
    cultures: list[SearchContentItem]
    restaurants: list[SearchContentItem]
    festivals: list[SearchContentItem]
    posts: list[SearchPostItem]