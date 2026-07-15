from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.models.regional_content import RegionalContent
from app.schemas.home import HomeResponse


router = APIRouter(
    prefix="/api/home",
    tags=["home"],
)


@router.get(
    "",
    response_model=HomeResponse,
)
def get_home(
    db: Session = Depends(get_db),
):
    categories = [
        "ATTRACTION",
        "CULTURE",
        "RESTAURANT",
        "FESTIVAL",
    ]

    random_contents = []

    for category in categories:
        content = (
            db.query(RegionalContent)
            .filter(
                RegionalContent.category == category
            )
            .order_by(func.random())
            .first()
        )

        if content:
            random_contents.append(content)

    recent_posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(5)
        .all()
    )

    popular_posts = (
        db.query(Post)
        .order_by(
            Post.view_count.desc(),
            Post.created_at.desc(),
        )
        .limit(5)
        .all()
    )

    return {
        "random_contents": random_contents,
        "recent_posts": recent_posts,
        "popular_posts": popular_posts,
    }