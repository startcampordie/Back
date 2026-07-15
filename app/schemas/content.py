from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ContentResponse(BaseModel):
    id: int
    category: str
    tag: str | None
    tags: list[str]
    title: str
    address: str | None
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_names(cls, value: Any) -> list[str]:
        if value is None:
            return []

        return [
            item if isinstance(item, str) else item.tag
            for item in value
        ]


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
