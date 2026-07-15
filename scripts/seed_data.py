import json
import os
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.regional_content import RegionalContent


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")


FILES = [
    (
        "광주_전라권_문화시설.json",
        "CULTURE",
        "체험하기 좋은",
    ),
    (
        "광주_전라권_관광지.json",
        "ATTRACTION",
        "자연을 즐기기 좋은",
    ),
    (
        "광주_전라권_음식점.json",
        "RESTAURANT",
        "가족과 함께하기 좋은",
    ),
    (
        "광주_전라권_축제공연행사.json",
        "FESTIVAL",
        "활기차게 즐기기 좋은",
    ),
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
    deleted_count = (
        db.query(RegionalContent)
        .delete(synchronize_session=False)
    )
    db.commit()

    print(f"기존 지역정보 {deleted_count}개 삭제 완료")

    inserted_count = 0

    for filename, category, tag in FILES:
        data = load_json(filename)
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

            content = RegionalContent(
                content_id=content_id,
                category=category,
                tag=tag,
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

            db.add(content)
            inserted_count += 1

    db.commit()

    print(f"전체 지역정보 {inserted_count}개 적재 완료")


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