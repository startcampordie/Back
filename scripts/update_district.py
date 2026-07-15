import re
import sqlite3


DATABASE_PATH = "localhub.db"


def extract_district(
    address: str | None,
) -> str | None:
    if not address:
        return None

    # 주소에서 ○○시, ○○군, ○○구 형태를 모두 추출
    areas = re.findall(
        r"([가-힣]+(?:시|군|구))(?=[\s,()]|$)",
        address,
    )

    # 광역 행정구역은 district 후보에서 제외
    excluded_suffixes = (
        "특별시",
        "광역시",
        "특별자치시",
    )

    districts = [
        area
        for area in areas
        if not area.endswith(excluded_suffixes)
    ]

    if not districts:
        return None

    return " ".join(districts)


connection = sqlite3.connect(
    DATABASE_PATH,
)

cursor = connection.cursor()

rows = cursor.execute(
    """
    SELECT id, address
    FROM regional_contents
    """
).fetchall()

updated_count = 0
failed_count = 0

for content_id, address in rows:
    district = extract_district(address)

    if district:
        # "전주시 완산구"처럼 여러 단어이면
        # 첫 번째 단어인 "전주시"만 저장
        district = district.split()[0]

        cursor.execute(
            """
            UPDATE regional_contents
            SET district = ?
            WHERE id = ?
            """,
            (
                district,
                content_id,
            ),
        )

        updated_count += 1

    else:
        failed_count += 1

connection.commit()
connection.close()

print(
    f"district 업데이트 완료: "
    f"{updated_count}건"
)

print(
    f"district 추출 실패: "
    f"{failed_count}건"
)