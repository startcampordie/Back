from openai import OpenAI

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def make_regional_context(contents) -> str:
    """
    관광지·음식점·축제 검색 결과를
    OpenAI에 전달할 문자열로 변환합니다.
    """

    if not contents:
        return "검색 결과 없음"

    lines = []

    for index, content in enumerate(contents, start=1):
        lines.append(
            f"{index}. "
            f"이름: {content.title}, "
            f"주소: {content.address or '주소 정보 없음'}"
        )

    return "\n".join(lines)


def make_post_context(posts) -> str:
    """
    게시글은 본문을 전달하지 않고
    게시글 ID와 제목만 전달합니다.
    """

    if not posts:
        return "검색 결과 없음"

    lines = []

    for index, post in enumerate(posts, start=1):
        lines.append(
            f"{index}. "
            f"게시글 ID: {post.id}, "
            f"제목: {post.title}"
        )

    return "\n".join(lines)


def make_prompt(
    intent: str,
    message: str,
    context: str,
) -> str:
    return f"""
너는 광주 지역 정보를 안내하는 LocalHub 챗봇이다.

규칙:
- 아래 검색 결과만 사용해서 답변한다.
- 검색 결과에 없는 장소를 추가하지 않는다.
- 제공되지 않은 정보는 추측하지 않는다.
- 답변은 3문장 이내로 작성한다.
- 친절하고 간결한 한국어로 작성한다.
- 장소 정보에는 이름과 주소만 사용한다.
- 게시글 정보에는 게시글 제목만 사용한다.
- 검색 결과가 없으면 찾지 못했다고 안내한다.

선택한 검색 유형:
{intent}

검색 결과:
{context}

사용자 질문:
{message}
""".strip()


def generate_ai_answer(
    intent: str,
    message: str,
    context: str,
) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되지 않았습니다."
        )

    # 함수가 실행될 때 클라이언트를 만듭니다.
    # API 키가 없어도 FastAPI 서버 자체는 실행될 수 있습니다.
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    prompt = make_prompt(
        intent=intent,
        message=message,
        context=context,
    )

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
        max_output_tokens=300,
    )

    answer = response.output_text.strip()

    if not answer:
        raise RuntimeError(
            "OpenAI가 빈 답변을 반환했습니다."
        )

    return answer