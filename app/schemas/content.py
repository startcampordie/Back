from pydantic import BaseModel


class ContentResponse(BaseModel):
    id: int
    category: str
    tag: str | None
    title: str
    address: str | None
    image_url: str | None

    class Config:
        from_attributes = True



class ContentListResponse(BaseModel):
    page: int
    size: int
    total: int
    items: list[ContentResponse]