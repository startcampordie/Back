import re
from datetime import datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.post import Post
from app.models.regional_content import RegionalContent


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


def search_regional_contents(
    db: Session,
    message: str,
    limit: int = 5,
) -> list[RegionalContent]:
    category = detect_category(message)
    district = detect_district(message)
    keyword = extract_keyword(message)

    query = db.query(RegionalContent)

    if category:
        query = query.filter(
            RegionalContent.category == category
        )

    if district:
        query = query.filter(
            RegionalContent.district.contains(district)
        )

    if keyword:
        query = query.filter(
            or_(
                RegionalContent.title.contains(keyword),
                RegionalContent.address.contains(keyword),
                RegionalContent.tag.contains(keyword),
            )
        )

    return (
        query
        .order_by(func.random())
        .limit(limit)
        .all()
    )


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


def make_regional_answer(
    message: str,
    contents: list[RegionalContent],
) -> str:
    if not contents:
        return (
            "조건에 맞는 지역 정보를 찾지 못했습니다. "
            "지역명이나 장소 이름을 바꿔서 질문해 주세요."
        )

    category = detect_category(message)
    district = detect_district(message)

    condition_parts = []

    if district:
        condition_parts.append(district)

    if category:
        condition_parts.append(category)

    condition = " ".join(condition_parts)

    if condition:
        introduction = (
            f"{condition} 검색 결과를 알려드릴게요."
        )
    else:
        introduction = "관련 지역 정보를 알려드릴게요."

    item_lines = []

    for index, content in enumerate(contents, start=1):
        address = content.address or "주소 정보 없음"

        item_lines.append(
            f"{index}. {content.title} - {address}"
        )

    return introduction + "\n" + "\n".join(item_lines)


def make_post_answer(posts: list[Post]) -> str:
    if not posts:
        return (
            "관련된 커뮤니티 게시글을 찾지 못했습니다. "
            "다른 검색어로 질문해 주세요."
        )

    item_lines = []

    for index, post in enumerate(posts, start=1):
        item_lines.append(
            f"{index}. {post.title} "
            f"(조회수 {post.view_count})"
        )

    return (
        "관련 커뮤니티 게시글을 찾았습니다.\n"
        + "\n".join(item_lines)
    )


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
    user_message: str,
) -> dict:
    intent = detect_intent(user_message)

    save_message(
        db=db,
        session_id=session.session_id,
        role="user",
        content=user_message,
        intent=intent,
    )

    references = []

    if intent == "post_search":
        posts = search_posts(
            db=db,
            message=user_message,
        )

        answer = make_post_answer(posts)

        references = [
            {
                "type": "post",
                "id": post.id,
                "title": post.title,
                "category": None,
                "address": None,
                "telephone": None,
            }
            for post in posts
        ]

    elif intent == "festival_schedule":
        answer = (
            "현재 보유한 축제 데이터에는 행사 시작일과 "
            "종료일이 포함되어 있지 않습니다. "
            "축제 목록과 위치 정보는 안내할 수 있습니다."
        )

    elif intent in [
        "regional_content_search",
        "telephone_search",
        "location_search",
    ]:
        contents = search_regional_contents(
            db=db,
            message=user_message,
        )

        answer = make_regional_answer(
            message=user_message,
            contents=contents,
        )

        references = [
            {
                "type": "regional_content",
                "id": content.id,
                "title": content.title,
                "category": content.category,
                "address": content.address,
                "telephone": content.telephone,
            }
            for content in contents
        ]

    else:
        answer = (
            "관광지, 맛집, 축제 또는 커뮤니티 게시글에 "
            "대해 질문해 주세요. 예를 들어 "
            "'북구 관광지 추천해줘'라고 질문할 수 있습니다."
        )

    assistant_message = save_message(
        db=db,
        session_id=session.session_id,
        role="assistant",
        content=answer,
        intent=intent,
    )

    extend_session(session)

    db.commit()
    db.refresh(assistant_message)

    return {
        "session_id": session.session_id,
        "intent": intent,
        "answer": answer,
        "references": references,
        "created_at": assistant_message.created_at,
    }