import random
from datetime import datetime, timedelta

from app.core.database import Base, SessionLocal, engine
from app.models.post import Post


POST_COUNT = 100
DUMMY_PASSWORD = "1234"
RANDOM_SEED = 20260716


PLACES = [
    "광주", "전주", "여수", "순천", "담양", "목포", "군산", "남원",
    "고창", "보성", "해남", "완도", "구례", "진도", "무주", "부안",
]

TOPICS = [
    "주말 여행 코스", "현지 맛집", "조용한 카페", "가족 나들이",
    "데이트 장소", "드라이브 코스", "야경 명소", "산책하기 좋은 곳",
    "비 오는 날 갈 곳", "대중교통 여행", "사진 찍기 좋은 곳", "지역 축제",
]

TITLE_PATTERNS = [
    "{place} {topic} 추천 부탁드려요",
    "{place}에서 다녀온 {topic} 후기",
    "{place} {topic} 정보 공유합니다",
    "처음 가는 {place}, {topic} 어디가 좋을까요?",
    "이번 주말 {place} {topic}을 찾고 있어요",
    "{place} 주민분들께 {topic} 질문드립니다",
]

CONTENT_PATTERNS = [
    (
        "이번 주말에 {place}에 방문할 예정입니다. {topic} 위주로 둘러보고 싶은데 "
        "직접 다녀오신 분들의 추천을 받고 싶어요. 주차나 이동 방법도 함께 "
        "알려주시면 감사하겠습니다."
    ),
    (
        "최근 {place}에서 {topic}을 즐기고 왔습니다. 생각보다 한적하고 분위기가 "
        "좋아서 여유롭게 시간을 보내기 좋았어요. 오전에 방문하면 조금 더 편하게 "
        "둘러볼 수 있을 것 같습니다."
    ),
    (
        "친구들과 {place} 여행을 준비하면서 {topic}을 알아보고 있습니다. 관광객에게 "
        "유명한 곳도 좋지만 현지 분들이 자주 찾는 장소가 있다면 소개해주세요."
    ),
    (
        "가족과 함께 {place}에 다녀오려고 합니다. {topic}과 가까운 식당이나 카페도 "
        "함께 방문하고 싶은데 이동 동선이 괜찮은 코스가 있을까요?"
    ),
    (
        "차 없이 {place}를 여행할 계획입니다. 대중교통이나 도보로 이동할 수 있는 "
        "{topic} 관련 장소를 찾고 있어요. 실제 방문 경험이 있다면 공유 부탁드립니다."
    ),
    (
        "지난번 {place} 방문 때 {topic}을 제대로 즐기지 못해서 다시 가보려고 합니다. "
        "방문하기 좋은 시간대와 주변에서 같이 둘러볼 장소를 추천해주세요."
    ),
]


def build_posts(count: int) -> list[Post]:
    random_generator = random.Random(RANDOM_SEED)
    now = datetime.now()
    posts: list[Post] = []
    used_titles: set[str] = set()

    while len(posts) < count:
        place = random_generator.choice(PLACES)
        topic = random_generator.choice(TOPICS)
        title = random_generator.choice(TITLE_PATTERNS).format(
            place=place,
            topic=topic,
        )

        if title in used_titles:
            continue

        used_titles.add(title)
        content = random_generator.choice(CONTENT_PATTERNS).format(
            place=place,
            topic=topic,
        )
        created_at = now - timedelta(
            days=random_generator.randint(0, 89),
            hours=random_generator.randint(0, 23),
            minutes=random_generator.randint(0, 59),
        )

        posts.append(
            Post(
                title=title,
                content=content,
                password=DUMMY_PASSWORD,
                view_count=random_generator.randint(0, 500),
                created_at=created_at,
                updated_at=created_at,
            )
        )

    return posts


def seed_posts(count: int = POST_COUNT) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_count = db.query(Post).count()

        if existing_count > 0:
            print(
                f"게시글이 이미 {existing_count}개 존재합니다. "
                "기존 게시글 보호를 위해 생성을 중단합니다."
            )
            return

        db.add_all(build_posts(count))
        db.commit()

        print(f"초기 게시글 {count}개를 생성했습니다.")
        print(f"수정 및 삭제용 공통 비밀번호: {DUMMY_PASSWORD}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_posts()
