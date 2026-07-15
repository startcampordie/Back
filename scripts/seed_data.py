import json
import os
import random
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.regional_content import RegionalContent
from app.models.regional_content_tag import RegionalContentTag


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")


FILES = [
    (
        "광주_전라권_문화시설.json",
        "CULTURE",
    ),
    (
        "광주_전라권_관광지.json",
        "ATTRACTION",
    ),
    (
        "광주_전라권_음식점.json",
        "RESTAURANT",
    ),
    (
        "광주_전라권_축제공연행사.json",
        "FESTIVAL",
    ),
]


ADDITIONAL_TAGS = [
    "조용한",
    "연인",
    "아이",
    "가족",
    "친구",
    "혼자",
    "사진",
    "자연",
    "체험",
    "활기찬",
]


def load_json(filename: str) -> dict[str, Any]:
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"JSON 파일을 찾을 수 없습니다: {path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def insert_contents(db: Session) -> None:
    datasets = [
        (filename, category, load_json(filename))
        for filename, category in FILES
    ]

    db.query(RegionalContentTag).delete(
        synchronize_session=False
    )

    deleted_count = (
        db.query(RegionalContent)
        .delete(synchronize_session=False)
    )

    print(f"기존 지역정보 {deleted_count}개 삭제 완료")

    inserted_count = 0
    inserted_tag_count = 0
    random_generator = random.Random()

    for filename, category, data in datasets:
        items = data.get("items", [])

        print(
            filename,
            "데이터 개수:",
            len(items),
        )

        for item in items:
            content_id = str(
                item.get("contentid", "")
            ).strip()

            title = str(
                item.get("title", "")
            ).strip()

            if not content_id or not title:
                continue

            selected_tags = random_generator.sample(
                ADDITIONAL_TAGS,
                random_generator.choice((2, 3)),
            )

            content = RegionalContent(
                content_id=content_id,
                category=category,
                tag=selected_tags[0],
                title=title,
                address=item.get("addr1") or None,
                address_detail=item.get("addr2") or None,
                district=None,
                image_url=item.get("firstimage") or None,
                image_thumbnail_url=(
                    item.get("firstimage2") or None
                ),
                longitude=to_float(item.get("mapx")),
                latitude=to_float(item.get("mapy")),
                telephone=item.get("tel") or None,
                original_cat1=item.get("cat1") or None,
                original_cat2=item.get("cat2") or None,
                original_cat3=item.get("cat3") or None,
            )

            content.tags = [
                RegionalContentTag(tag=tag_name)
                for tag_name in selected_tags
            ]

            db.add(content)
            inserted_count += 1
            inserted_tag_count += len(selected_tags)

    db.commit()

    print(f"전체 지역정보 {inserted_count}개 적재 완료")
    print(f"전체 다중 태그 {inserted_tag_count}개 적재 완료")


def main() -> None:
    db = SessionLocal()

    try:
        insert_contents(db)

    except Exception as error:
        db.rollback()
        print("데이터 적재 실패:", error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
