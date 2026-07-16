import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.regional_content import RegionalContent
from app.models.regional_content_tag import RegionalContentTag
from app.schemas.content import ContentListResponse


router = APIRouter(
    prefix="/api/contents",
    tags=["contents"],
)


ALLOWED_CATEGORIES = {
    "ALL",
    "ATTRACTION",
    "CULTURE",
    "RESTAURANT",
    "FESTIVAL",
}


@router.get(
    "",
    response_model=ContentListResponse,
)
def get_contents(
    category: str = Query(
        default="ALL",
        description=(
            "ALL, ATTRACTION, CULTURE, "
            "RESTAURANT, FESTIVAL"
        ),
    ),
    # 기존 단일 태그 요청 코드:
    # tag: str | None = Query(
    #     default=None,
    #     description="추천 태그",
    # ),
    tags: list[str] = Query(
        default=[],
        description="추천 태그 목록(선택한 태그 중 하나 이상 일치)",
    ),
    keyword: str | None = Query(
        default=None,
        description="장소 이름 또는 주소 검색",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="현재 페이지",
    ),
    size: int = Query(
        default=5,
        ge=1,
        le=50,
        description="페이지당 데이터 수",
    ),
    db: Session = Depends(get_db),
):
    category = category.upper().strip()

    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 카테고리입니다.",
        )

    query = db.query(RegionalContent)

    # 카테고리 필터
    # ALL이면 카테고리 조건을 추가하지 않는다.
    if category != "ALL":
        query = query.filter(
            RegionalContent.category == category
        )

    # 기존 단일 태그 필터 코드:
    # if tag:
    #     normalized_tag = tag.strip()
    #
    #     if normalized_tag:
    #         query = query.filter(
    #             RegionalContent.tags.any(
    #                 RegionalContentTag.tag == normalized_tag
    #             )
    #         )
    #     else:
    #         tag = None

    # 다중 태그 OR 필터
    # 카테고리·검색어 조건과는 AND로 결합하고,
    # 선택된 태그끼리는 하나 이상 일치하면 조회합니다.
    normalized_tags = list(dict.fromkeys(
        tag.strip()
        for tag in tags
        if tag.strip()
    ))

    if normalized_tags:
        query = query.filter(
            RegionalContent.tags.any(
                RegionalContentTag.tag.in_(normalized_tags)
            )
        )

    # 장소 이름 또는 주소 검색
    if keyword:
        normalized_keyword = keyword.strip()

        if normalized_keyword:
            query = query.filter(
                or_(
                    RegionalContent.title.contains(
                        normalized_keyword
                    ),
                    RegionalContent.address.contains(
                        normalized_keyword
                    ),
                    RegionalContent.address_detail.contains(
                        normalized_keyword
                    ),
                )
            )
        else:
            keyword = None

    # 검색 조건 적용 후 전체 결과 개수
    total_elements = query.count()

    # 전체 페이지 수
    total_pages = (
        math.ceil(total_elements / size)
        if total_elements > 0
        else 0
    )

    # 요청 페이지가 전체 페이지보다 큰 경우에는 빈 목록 반환
    offset = (page - 1) * size

    items = (
        query
        .order_by(RegionalContent.id.asc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return {
        "category": category,
        # 기존 단일 태그 응답 필드는 호환성을 위해 유지합니다.
        "selected_tag": (
            normalized_tags[0]
            if len(normalized_tags) == 1
            else None
        ),
        "selected_tags": normalized_tags,
        "keyword": keyword,
        "page": page,
        "size": size,
        "total_elements": total_elements,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "items": items,
    }
