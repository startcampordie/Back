import logging

from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


logger = logging.getLogger(__name__)

OPENAI_CONTEXT_LIMIT = 10
AI_RECOMMENDATION_LIMIT = 5


class AIRecommendation(BaseModel):
    """
    AI가 선택한 검색 결과 한 건입니다.
    """

    id: int = Field(
        description=(
            "서버가 제공한 검색 결과의 ID"
        ),
    )

    reason: str = Field(
        min_length=1,
        max_length=100,
        description=(
            "해당 검색 결과를 선택한 이유. "
            "제공된 이름과 주소만 근거로 작성합니다."
        ),
    )


class AIChatOutput(BaseModel):
    """
    OpenAI가 반환해야 하는 전체 구조입니다.
    """

    answer: str = Field(
        min_length=1,
        max_length=300,
        description=(
            "사용자에게 보여줄 전체 안내 문장"
        ),
    )

    recommendations: list[AIRecommendation] = Field(
        max_length=AI_RECOMMENDATION_LIMIT,
        description=(
            "선택한 검색 결과와 선택 이유. "
            "최대 5건"
        ),
    )


def make_regional_context(contents) -> str:
    """
    지역 정보 검색 결과를 ID와 함께 OpenAI에 전달합니다.
    """

    if not contents:
        return "검색 결과 없음"

    lines = []

    for index, content in enumerate(
        contents[:OPENAI_CONTEXT_LIMIT],
        start=1,
    ):
        lines.append(
            f"{index}. "
            f"ID: {content.id} | "
            f"이름: {content.title} | "
            f"주소: {content.address or '주소 정보 없음'}"
        )

    return "\n".join(lines)


def make_post_context(posts) -> str:
    """
    게시글 본문은 제외하고 ID와 제목만 전달합니다.
    """

    if not posts:
        return "검색 결과 없음"

    lines = []

    for index, post in enumerate(
        posts[:OPENAI_CONTEXT_LIMIT],
        start=1,
    ):
        lines.append(
            f"{index}. "
            f"ID: {post.id} | "
            f"제목: {post.title}"
        )

    return "\n".join(lines)


def make_prompt(
    intent: str,
    message: str,
    context: str,
) -> str:
    return (
        f"검색 유형:\n{intent}\n\n"
        f"서버 검색 결과:\n{context}\n\n"
        f"사용자 질문:\n{message}"
    )


def generate_ai_answer(
    question: str,
    intent: str,
    regional_context: str,
) -> AIChatOutput:
    """
    전체 안내 문장과 장소별 ID·선택 이유를 반환합니다.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되지 않았습니다."
        )

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=20.0,
        max_retries=0,
    )

    response = client.responses.parse(
        model=OPENAI_MODEL,
        reasoning={
            "effort": "minimal",
        },
        instructions=(
            "너는 광주·전라 지역 정보를 안내하는 "
            "LocalHub 챗봇이다. "
            "반드시 서버가 제공한 검색 결과만 사용한다. "
            "검색 결과에 없는 장소나 게시글을 추가하지 않는다. "
            "제공되지 않은 정보는 추측하지 않는다. "
            "answer에는 사용자에게 직접 추천하는 형태로 작성하세요. "
            "answer에는 개별 장소의 상세 설명을 작성하지 않는다. "
            "선택한 검색 결과는 recommendations에 넣는다. "
            "recommendations의 id는 서버 검색 결과에 "
            "있는 ID만 사용한다. "
            "reason에는 장소명, 추천 이유, 방문 상황에 맞는 설명을 포함하세요. "
            "시설, 메뉴, 가격, 운영시간 등 제공되지 않은 "
            "정보는 작성하지 않는다. "
            "recommendations는 최대 5개로 제한한다. "
            "답변은 친절하고 간결한 한국어로 작성한다."
        ),
        input=make_prompt(
            intent=intent,
            message=question,
            context=regional_context,
        ),
        text_format=AIChatOutput,
        max_output_tokens=1000,
    )

    logger.info(
        "OpenAI response_id=%s, status=%s, "
        "incomplete=%s, usage=%s",
        response.id,
        response.status,
        response.incomplete_details,
        response.usage,
    )

    result = response.output_parsed

    if result is None:
        reason = getattr(
            response.incomplete_details,
            "reason",
            None,
        )

        raise RuntimeError(
            "OpenAI 구조화 응답 없음 "
            f"(status={response.status}, reason={reason})"
        )

    answer = result.answer.strip()

    if not answer:
        raise RuntimeError(
            "OpenAI가 빈 답변을 반환했습니다."
        )

    return AIChatOutput(
        answer=answer,
        recommendations=result.recommendations,
    )