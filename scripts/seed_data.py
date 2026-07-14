import json
import os

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.regional_content import RegionalContent


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")


FILES = [
    (
        "광주_전라권_관광지.json",
        "ATTRACTION",
        "자연을 즐기기 좋은"
    ),
    (
        "광주_전라권_음식점.json",
        "RESTAURANT",
        "가족과 함께하기 좋은"
    ),
    (
        "광주_전라권_축제공연행사.json",
        "FESTIVAL",
        "활기찬 분위기"
    ),
]


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def insert_contents(db: Session):

    for filename, category, tag in FILES:

        data = load_json(filename)

        print(
            filename,
            "데이터 개수:",
            data["total"]
        )

        for item in data["items"]:

            content = RegionalContent(
                content_id=item["contentid"],
                category=category,
                tag=tag,

                title=item["title"],

                address=item.get("addr1"),
                address_detail=item.get("addr2"),

                image_url=item.get("firstimage"),
                image_thumbnail_url=item.get("firstimage2"),

                longitude=float(item["mapx"])
                if item.get("mapx")
                else None,

                latitude=float(item["mapy"])
                if item.get("mapy")
                else None,

                telephone=item.get("tel"),

                original_cat1=item.get("cat1"),
                original_cat2=item.get("cat2"),
                original_cat3=item.get("cat3"),
            )


            db.add(content)


    db.commit()


def main():

    db = SessionLocal()

    try:
        insert_contents(db)

    finally:
        db.close()


if __name__ == "__main__":
    main()