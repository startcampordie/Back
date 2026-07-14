from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.regional_content import RegionalContent
from app.schemas.content import ContentListResponse


router = APIRouter(
    prefix="/api/contents",
    tags=["contents"]
)



@router.get(
    "",
    response_model=ContentListResponse
)
def get_contents(
    category: str | None = None,
    tag: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    size: int = 5,
    db: Session = Depends(get_db)
):

    query = db.query(RegionalContent)


    # 1. 카테고리 필터
    if category:
        query = query.filter(
            RegionalContent.category == category
        )


    # 2. 태그 필터
    if tag:
        query = query.filter(
            RegionalContent.tag == tag
        )


    # 3. 검색
    if keyword:
        query = query.filter(
            RegionalContent.title.contains(keyword)
        )


    # 전체 개수
    total = query.count()


    # 페이징
    contents = (
        query
        .offset((page-1) * size)
        .limit(size)
        .all()
    )


    return {
        "page": page,
        "size": size,
        "total": total,
        "items": contents
    }