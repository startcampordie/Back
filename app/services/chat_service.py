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

DB_SEARCH_LIMIT = 10
OPENAI_CONTEXT_LIMIT = 10
RESPONSE_REFERENCE_LIMIT = 5

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

def select_results_by_ids(
    results,
    selected_ids: list[int],
    limit: int = RESPONSE_REFERENCE_LIMIT,
):
    """
    OpenAI가 선택한 ID를 서버 검색 결과와 대조합니다.

    - 검색 후보에 없는 ID 제거
    - 중복 ID 제거
    - OpenAI가 선택한 순서 유지
    - 최대 5건 제한
    """

    result_map = {
        result.id: result
        for result in results
    }

    selected_results = []
    seen_ids = set()

    for selected_id in selected_ids:
        if selected_id in seen_ids:
            continue

        result = result_map.get(selected_id)

        if result is None:
            logger.warning(
                "OpenAI가 검색 후보에 없는 ID를 선택함: %s",
                selected_id,
            )
            continue

        seen_ids.add(selected_id)
        selected_results.append(result)

        if len(selected_results) >= limit:
            break

    return selected_results

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

def select_recommended_results(
    results,
    recommendations,
    limit: int = RESPONSE_REFERENCE_LIMIT,
):
    """
    AI가 선택한 ID를 서버 검색 결과와 대조합니다.

    반환값:
    - selected_results: 검증된 DB 객체
    - reasons_by_id: ID별 AI 선택 이유
    """

    result_map = {
        result.id: result
        for result in results
    }

    selected_results = []
    reasons_by_id = {}
    seen_ids = set()

    for recommendation in recommendations:
        selected_id = recommendation.id

        if selected_id in seen_ids:
            continue

        result = result_map.get(selected_id)

        if result is None:
            logger.warning(
                "OpenAI가 검색 후보에 없는 ID를 선택함: %s",
                selected_id,
            )
            continue

        reason = recommendation.reason.strip()

        if not reason:
            continue

        seen_ids.add(selected_id)
        selected_results.append(result)
        reasons_by_id[selected_id] = reason

        if len(selected_results) >= limit:
            break

    return selected_results, reasons_by_id

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

    # 2. DB 검색
    if intent == "community_post":
        total, results = search_posts(
            db=db,
            message=message,
        )

        candidates = results[:OPENAI_CONTEXT_LIMIT]
        context = make_post_context(candidates)
        reference_builder = make_post_references

    else:
        total, results = search_regional_contents(
            db=db,
            intent=intent,
            message=message,
        )

        candidates = results[:OPENAI_CONTEXT_LIMIT]
        context = make_regional_context(candidates)
        reference_builder = make_content_references

    # OpenAI 실패 시 사용할 기본 검색 결과
    selected_results = candidates[
        :RESPONSE_REFERENCE_LIMIT
    ]
    reasons_by_id = {}

    # 3. 검색 결과가 없으면 OpenAI 호출 생략
    if not candidates:
        answer = make_fallback_answer(
            intent=intent,
            total=total,
            results=candidates,
        )

    else:
        try:
            # 4. 구조화된 OpenAI 응답 생성
            ai_result = generate_ai_answer(
                intent=intent,
                question=message,
                regional_context=context,
            )

            (
                ai_selected_results,
                ai_reasons_by_id,
            ) = select_recommended_results(
                results=candidates,
                recommendations=(
                    ai_result.recommendations
                ),
            )

            # 5. 유효한 추천 항목이 있을 때만 AI 응답 사용
            if ai_selected_results:
                answer = ai_result.answer
                selected_results = (
                    ai_selected_results
                )
                reasons_by_id = (
                    ai_reasons_by_id
                )

            else:
                logger.warning(
                    "OpenAI가 유효한 검색 결과를 "
                    "선택하지 않았습니다."
                )

                answer = make_fallback_answer(
                    intent=intent,
                    total=total,
                    results=candidates,
                )

        except Exception:
            logger.exception(
                "OpenAI 답변 생성 실패"
            )

            answer = make_fallback_answer(
                intent=intent,
                total=total,
                results=candidates,
            )

    # 6. 장소 정보와 AI 선택 이유 결합
    references = reference_builder(
        selected_results,
        reasons_by_id,
    )

    # 7. 챗봇 답변 저장
    assistant_message = save_message(
        db=db,
        session_id=session.session_id,
        role="assistant",
        content=answer,
        intent=intent,
    )

    # 8. 세션 만료일 연장
    extend_session(session)

    db.commit()
    db.refresh(assistant_message)

    # 9. API 응답
    return {
        "session_id": session.session_id,
        "intent": intent,
        "answer": answer,
        "total": total,
        "references": references,
        "created_at": (
            assistant_message.created_at
        ),
    }

def make_content_references(
    contents,
    reasons_by_id: dict[int, str] | None = None,
) -> list[dict]:
    """
    지역 정보와 해당 ID의 AI 선택 이유를 반환합니다.
    """

    reasons_by_id = reasons_by_id or {}

    return [
        {
            "type": "regional_content",
            "id": content.id,
            "title": content.title,
            "category": content.category,
            "address": content.address,
            "telephone": content.telephone,
            "image_url": content.image_url,
            "image_thumbnail_url": (
                content.image_thumbnail_url
            ),
            "reason": reasons_by_id.get(
                content.id
            ),
            "view_count": None,
        }
        for content in contents[
            :RESPONSE_REFERENCE_LIMIT
        ]
    ]

def make_post_references(
    posts,
    reasons_by_id: dict[int, str] | None = None,
) -> list[dict]:
    """
    게시글과 해당 ID의 AI 선택 이유를 반환합니다.
    """

    reasons_by_id = reasons_by_id or {}

    return [
        {
            "type": "post",
            "id": post.id,
            "title": post.title,
            "category": None,
            "address": None,
            "telephone": None,
            "image_url": None,
            "image_thumbnail_url": None,
            "reason": reasons_by_id.get(
                post.id
            ),
            "view_count": post.view_count,
        }
        for post in posts[
            :RESPONSE_REFERENCE_LIMIT
        ]
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