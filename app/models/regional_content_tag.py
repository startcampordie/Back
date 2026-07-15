from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.regional_content import RegionalContent


class RegionalContentTag(Base):
    __tablename__ = "regional_content_tags"
    __table_args__ = (
        UniqueConstraint(
            "regional_content_id",
            "tag",
            name="uq_regional_content_tag",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    regional_content_id: Mapped[int] = mapped_column(
        ForeignKey(
            "regional_contents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    tag: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    regional_content: Mapped["RegionalContent"] = relationship(
        back_populates="tags",
    )
