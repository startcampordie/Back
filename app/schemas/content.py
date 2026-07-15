from pydantic import BaseModel, ConfigDict


class ContentResponse(BaseModel):
    id: int
    category: str
    tag: str | None
    title: str
    address: str | None
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class ContentListResponse(BaseModel):
    category: str
    selected_tag: str | None
    keyword: str | None

    page: int
    size: int
    total_elements: int
    total_pages: int
    has_previous: bool
    has_next: bool

    items: list[ContentResponse]