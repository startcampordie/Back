import re
from datetime import datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.post import Post
from app.models.regional_content import RegionalContent
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.services.openai_service import (
    generate_ai_answer,
    make_post_context,
    make_regional_context,
)
from app.services.search_service import (
    search_posts,
    search_regional_contents,
)

logger = logging.getLogger(__name__)


CATEGORY_KEYWORDS = {
    "관광지": [
        "관광지",
        "관광",
        "가볼 곳",
        "가볼곳",
        "명소",
        "여행",
    ],
    "음식점": [
        "음식점",
        "맛집",
        "식당",
        "먹을 곳",
        "먹을곳",
    ],
    "축제공연행사": [
        "축제",
        "공연",
        "행사",
        "이벤트",
    ],
}

DISTRICTS = [
    "동구",
    "서구",
    "남구",
    "북구",
    "광산구",
]

POST_KEYWORDS = [
    "게시글",
    "게시판",
    "커뮤니티",
    "글 찾아",
    "글 검색",
    "후기 글",
]

SCHEDULE_KEYWORDS = [
    "일정",
    "언제",
    "시작일",
    "종료일",
    "기간",
    "오늘 열리는",
]

TELEPHONE_KEYWORDS = [
    "전화번호",
    "연락처",
    "전화",
]

LOCATION_KEYWORDS = [
    "주소",
    "위치",
    "어디",
]

STOP_WORDS = [
    "광주",
    "전라권",
    "추천",
    "알려줘",
    "알려주세요",
    "찾아줘",
    "찾아주세요",
    "검색해줘",
    "검색해주세요",
    "유명한",
    "관련",
    "있는",
    "가까운",
    "어디야",
    "어디",
    "정보",
    "대한",
    "좀",
]


def create_chat_session(db: Session) -> ChatSession:
    session = ChatSession()

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_chat_session(
    db: Session,
    session_id: str,
) -> ChatSession | None:
    return (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id)
        .first()
    )


def is_session_expired(session: ChatSession) -> bool:
    return session.expires_at < datetime.now()


def extend_session(session: ChatSession) -> None:
    now = datetime.now()

    session.last_active_at = now
    session.expires_at = now + timedelta(days=7)


def contains_any(
    message: str,
    keywords: list[str],
) -> bool:
    return any(
        keyword in message
        for keyword in keywords
    )


def detect_category(message: str) -> str | None:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if contains_any(message, keywords):
            return category

    return None


def detect_district(message: str) -> str | None:
    for district in DISTRICTS:
        if district in message:
            return district

    return None


def detect_intent(message: str) -> str:
    if contains_any(message, POST_KEYWORDS):
        return "post_search"

    if contains_any(message, SCHEDULE_KEYWORDS):
        return "festival_schedule"

    if contains_any(message, TELEPHONE_KEYWORDS):
        return "telephone_search"

    if contains_any(message, LOCATION_KEYWORDS):
        return "location_search"

    if detect_category(message):
        return "regional_content_search"

    return "unknown"


def extract_keyword(message: str) -> str | None:
    keyword = message

    removable_words = (
        STOP_WORDS
        + DISTRICTS
        + POST_KEYWORDS
        + SCHEDULE_KEYWORDS
        + TELEPHONE_KEYWORDS
        + LOCATION_KEYWORDS
    )

    for category_keywords in CATEGORY_KEYWORDS.values():
        removable_words.extend(category_keywords)

    # 긴 문구부터 제거
    removable_words = sorted(
        set(removable_words),
        key=len,
        reverse=True,
    )

    for word in removable_words:
        keyword = keyword.replace(word, " ")

    keyword = re.sub(
        r"[^가-힣a-zA-Z0-9]",
        " ",
        keyword,
    )

    keyword = re.sub(
        r"\s+",
        " ",
        keyword,
    ).strip()

    if len(keyword) < 2:
        return None

    return keyword


def search_posts(
    db: Session,
    message: str,
    limit: int = 5,
) -> list[Post]:
    keyword = extract_keyword(message)

    query = db.query(Post)

    if keyword:
        query = query.filter(
            or_(
                Post.title.contains(keyword),
                Post.content.contains(keyword),
            )
        )

    return (
        query
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )


# def make_regional_answer(
#     message: str,
#     contents: list[RegionalContent],
# ) -> str:
#     if not contents:
#         return (
#             "조건에 맞는 지역 정보를 찾지 못했습니다. "
#             "지역명이나 장소 이름을 바꿔서 질문해 주세요."
#         )

#     category = detect_category(message)
#     district = detect_district(message)

#     condition_parts = []

#     if district:
#         condition_parts.append(district)

#     if category:
#         condition_parts.append(category)

#     condition = " ".join(condition_parts)

#     if condition:
#         introduction = (
#             f"{condition} 검색 결과를 알려드릴게요."
#         )
#     else:
#         introduction = "관련 지역 정보를 알려드릴게요."

#     item_lines = []

#     for index, content in enumerate(contents, start=1):
#         address = content.address or "주소 정보 없음"

#         item_lines.append(
#             f"{index}. {content.title} - {address}"
#         )

#     return introduction + "\n" + "\n".join(item_lines)


# def make_post_answer(posts: list[Post]) -> str:
#     if not posts:
#         return (
#             "관련된 커뮤니티 게시글을 찾지 못했습니다. "
#             "다른 검색어로 질문해 주세요."
#         )

#     item_lines = []

#     for index, post in enumerate(posts, start=1):
#         item_lines.append(
#             f"{index}. {post.title} "
#             f"(조회수 {post.view_count})"
#         )

#     return (
#         "관련 커뮤니티 게시글을 찾았습니다.\n"
#         + "\n".join(item_lines)
#     )


def save_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    intent: str | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        intent=intent,
    )

    db.add(message)

    return message


def process_chat(
    db: Session,
    session: ChatSession,
    intent: str,
    message: str,
) -> dict:
    # 1. 사용자 메시지 저장
    save_message(
        db=db,
        session_id=session.session_id,
        role="user",
        content=message,
        intent=intent,
    )

    # 2. 검색 대상에 따라 DB 검색
    if intent == "community_post":
        total, results = search_posts(
            db=db,
            message=message,
        )

        context = make_post_context(results)
        references = make_post_references(results)

    else:
        total, results = search_regional_contents(
            db=db,
            intent=intent,
            message=message,
        )

        context = make_regional_context(results)
        references = make_content_references(results)

    # 3. 검색 결과가 없다면 OpenAI를 호출하지 않음
    if not results:
        answer = make_fallback_answer(
            intent=intent,
            total=total,
            results=results,
        )

    else:
        # 4. 검색 결과가 있을 때만 OpenAI 호출
        try:
            answer = generate_ai_answer(
                intent=intent,
                message=message,
                context=context,
            )

        except Exception:
            logger.exception(
                "OpenAI 답변 생성 실패"
            )

            answer = make_fallback_answer(
                intent=intent,
                total=total,
                results=results,
            )

    # 5. 챗봇 답변 저장
    assistant_message = save_message(
        db=db,
        session_id=session.session_id,
        role="assistant",
        content=answer,
        intent=intent,
    )

    # 6. 세션 만료 시각을 마지막 대화 기준 7일 연장
    extend_session(session)

    db.commit()
    db.refresh(assistant_message)

    # 7. API 응답
    return {
        "session_id": session.session_id,
        "intent": intent,
        "answer": answer,
        "total": total,
        "references": references,
        "created_at": assistant_message.created_at,
    }

def make_content_references(contents) -> list[dict]:
    """
    지역 정보는 ID, 이름, 카테고리, 주소만
    프론트에 반환합니다.
    """

    return [
        {
            "type": "regional_content",
            "id": content.id,
            "title": content.title,
            "category": content.category,
            "address": content.address,
            "telephone": None,
            "view_count": None,
        }
        for content in contents
    ]

def make_post_references(posts) -> list[dict]:
    """
    게시글 본문은 반환하지 않습니다.
    프론트는 ID를 이용해 상세 페이지로 이동합니다.
    """

    return [
        {
            "type": "post",
            "id": post.id,
            "title": post.title,
            "category": None,
            "address": None,
            "telephone": None,
            "view_count": post.view_count,
        }
        for post in posts
    ]


def make_fallback_answer(
    intent: str,
    total: int,
    results,
) -> str:
    """
    OpenAI 호출 실패 시 사용하는 기본 답변입니다.
    """

    if not results:
        return (
            "조건에 맞는 정보를 찾지 못했습니다. "
            "지역이나 검색어를 바꿔서 질문해 주세요."
        )

    intent_names = {
        "attraction": "관광지",
        "culture": "문화시설",
        "restaurant": "음식점",
        "festival": "축제·행사",
    }

    intent_name = intent_names.get(
        intent,
        "정보",
    )

    return (
        f"조건에 맞는 {intent_name} "
        f"{total}건 중 {len(results)}건을 "
        f"안내해 드릴게요."
    )