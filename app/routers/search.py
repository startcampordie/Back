from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.models.regional_content import RegionalContent
from app.schemas.search import SearchResponse


router = APIRouter(
    prefix="/api/search",
    tags=["search"],
)


def make_content_query(
    db: Session,
    category: str,
    keyword: str,
    district: str | None,
):
    query = (
        db.query(RegionalContent)
        .filter(RegionalContent.category == category)
    )

    query = query.filter(
        or_(
            RegionalContent.title.contains(keyword),
            RegionalContent.address.contains(keyword),
        )
    )

    if district:
        query = query.filter(
            RegionalContent.address.contains(district)
        )

    return query.limit(20).all()


@router.get(
    "",
    response_model=SearchResponse,
)
def search_all(
    keyword: str = Query(..., min_length=1),
    search_type: str = Query(
        default="ALL",
        description=(
            "ALL, ATTRACTION, CULTURE, "
            "RESTAURANT, FESTIVAL, POST"
        ),
    ),
    district: str | None = None,
    db: Session = Depends(get_db),
):
    search_type = search_type.upper()

    allowed_types = {
        "ALL",
        "ATTRACTION",
        "CULTURE",
        "RESTAURANT",
        "FESTIVAL",
        "POST",
    }

    if search_type not in allowed_types:
        search_type = "ALL"

    attractions = []
    cultures = []
    restaurants = []
    festivals = []
    posts = []

    if search_type in {"ALL", "ATTRACTION"}:
        attractions = make_content_query(
            db=db,
            category="ATTRACTION",
            keyword=keyword,
            district=district,
        )

    if search_type in {"ALL", "CULTURE"}:
        cultures = make_content_query(
            db=db,
            category="CULTURE",
            keyword=keyword,
            district=district,
        )

    if search_type in {"ALL", "RESTAURANT"}:
        restaurants = make_content_query(
            db=db,
            category="RESTAURANT",
            keyword=keyword,
            district=district,
        )

    if search_type in {"ALL", "FESTIVAL"}:
        festivals = make_content_query(
            db=db,
            category="FESTIVAL",
            keyword=keyword,
            district=district,
        )

    if search_type in {"ALL", "POST"}:
        post_query = db.query(Post).filter(
            or_(
                Post.title.contains(keyword),
                Post.content.contains(keyword),
            )
        )

        post_rows = (
            post_query
            .order_by(Post.created_at.desc())
            .limit(20)
            .all()
        )

        posts = [
            {
                "id": post.id,
                "title": post.title,
                "content_preview": (
                    post.content[:100]
                    if len(post.content) > 100
                    else post.content
                ),
                "created_at": post.created_at,
                "view_count": post.view_count,
            }
            for post in post_rows
        ]

    total_count = (
        len(attractions)
        + len(cultures)
        + len(restaurants)
        + len(festivals)
        + len(posts)
    )

    return {
        "keyword": keyword,
        "search_type": search_type,
        "district": district,
        "total_count": total_count,
        "attractions": attractions,
        "cultures": cultures,
        "restaurants": restaurants,
        "festivals": festivals,
        "posts": posts,
    }