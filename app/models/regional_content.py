from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.regional_content_tag import RegionalContentTag


class RegionalContent(Base):
    __tablename__ = "regional_contents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    content_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    tag: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    address_detail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_thumbnail_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    telephone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    original_cat1: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    original_cat2: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    original_cat3: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    tags: Mapped[list["RegionalContentTag"]] = relationship(
        back_populates="regional_content",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="RegionalContentTag.id",
    )
