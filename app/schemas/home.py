from datetime import datetime

from pydantic import BaseModel


class HomeContentItem(BaseModel):
    id: int
    category: str
    tag: str | None
    title: str
    address: str | None
    image_url: str | None

    class Config:
        from_attributes = True


class HomePostItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    view_count: int

    class Config:
        from_attributes = True


class HomeResponse(BaseModel):
    random_contents: list[HomeContentItem]
    recent_posts: list[HomePostItem]
    popular_posts: list[HomePostItem]