# <<<<<<<<<<<< 지역 정보 검색 시작 >>>>>>>>>>>>> #
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.regional_content import RegionalContent

CATEGORY_MAP = {
    "attraction": "ATTRACTION",
    "culture": "CULTURE",
    "restaurant": "RESTAURANT",
    "festival": "FESTIVAL",
}

DISTRICTS = [
    "동구",
    "서구",
    "남구",
    "북구",
    "광산구",
]

def extract_district(message: str) -> str | None:
    for district in DISTRICTS:
        if district in message:
            return district

    return None

def search_regional_contents(
    db: Session,
    intent: str,
    message: str,
):
    category = CATEGORY_MAP[intent]
    district = extract_district(message)

    query = db.query(RegionalContent).filter(
        RegionalContent.category == category
    )

    if district:
        query = query.filter(
            RegionalContent.district.contains(district)
        )

    total = query.count()

    candidates = (
        query
        .order_by(func.random())
        .limit(10)
        .all()
    )

    # 사용자에게 최종 표시할 결과
    results = candidates[:5]

    return total, results

# <<<<<<<<<<<< 지역 정보 검색 끝 >>>>>>>>>>>>> #
# <<<<<<<<<<<< 게시글 검색 시작 >>>>>>>>>>>>> #

from sqlalchemy import or_

from app.models.post import Post


POST_REMOVE_WORDS = [
    "관련",
    "게시글",
    "게시판",
    "커뮤니티",
    "글",
    "찾아줘",
    "찾아주세요",
    "검색해줘",
    "검색해주세요",
]


def extract_post_keyword(message: str) -> str | None:
    keyword = message

    for word in POST_REMOVE_WORDS:
        keyword = keyword.replace(word, " ")

    keyword = " ".join(keyword.split())

    return keyword or None


def search_posts(
    db: Session,
    message: str,
):
    keyword = extract_post_keyword(message)

    query = db.query(Post)

    if keyword:
        query = query.filter(
            or_(
                Post.title.contains(keyword),
                Post.content.contains(keyword),
            )
        )

    total = query.count()

    posts = (
        query
        .order_by(Post.created_at.desc())
        .limit(5)
        .all()
    )

    return total, posts

# <<<<<<<<<<<< 게시글 검색 끝 >>>>>>>>>>>>> #