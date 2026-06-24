import os
import time
import logging
from notion_client import Client
from notion_client.errors import APIResponseError


# =========================================================
# 로그 설정
# =========================================================
# Notion SDK의 WARNING 로그가 메일 결과물에 섞이지 않도록 숨김
logging.getLogger("notion_client").setLevel(logging.ERROR)


# =========================================================
# 기본 설정
# =========================================================

TOKEN = os.environ["NOTION_TOKEN"]

# 통합 프로젝트 DB / Data Source ID
TARGET_DB_ID = "395cbb1d-cbaa-829c-a5a4-878f6a7b9b7d"

# 테스트할 때만 숫자 입력. 전체 실행은 None.
TEST_LIMIT_PER_DB = None

# 더 이상 취합하지 않을 속성
EXCLUDED_PROPERTIES = {
    "중요도",
    "Priority",
    "priority",
}

SOURCE_PAGE_ID_PROP_CANDIDATES = [
    "원본 page ID",
    "원본 Page ID",
    "원본페이지ID",
    "원본 페이지 ID",
    "source_page_id",
    "Source Page ID",
]

SOURCE_DB_ID_PROP_CANDIDATES = [
    "원본 DB ID",
    "원본DB ID",
    "원본 데이터소스 ID",
    "source_db_id",
    "Source DB ID",
]

SOURCE_URL_PROP_CANDIDATES = [
    "원본 링크",
    "원본링크",
    "Source URL",
    "source_url",
    "URL",
]

SOURCE_DB_NAME_PROP_CANDIDATES = [
    "팀",
    "팀명",
    "부서",
    "원본 DB",
    "원본DB",
    "원본 DB명",
    "source_db",
    "Source DB",
]


SOURCE_DBS = [
    {"id": "366cbb1d-cbaa-8035-925a-000b1ddd6708", "team": "평택생산팀"},
    {"id": "366cbb1d-cbaa-8044-9bef-000bc920e796", "team": "재경/내부통제(ES)팀"},
    {"id": "366cbb1d-cbaa-8022-8c86-000bcbc581a5", "team": "내부통제팀"},
    {"id": "366cbb1d-cbaa-803b-9c86-000baf05603b", "team": "인사팀"},
    {"id": "366cbb1d-cbaa-80d8-a15c-000b0f1354f1", "team": "ESH팀"},
    {"id": "366cbb1d-cbaa-8064-b4c5-000bf7f43e67", "team": "총무팀"},
    {"id": "366cbb1d-cbaa-80a4-9920-000bb0c809a5", "team": "구매개발팀"},
    {"id": "366cbb1d-cbaa-80be-8b9d-000bd0ca2dae", "team": "영업관리팀"},
    {"id": "366cbb1d-cbaa-8026-ab8c-000b7fc774e3", "team": "PM팀"},
    {"id": "366cbb1d-cbaa-807a-97dd-000b3aca14a1", "team": "원가팀"},
    {"id": "366cbb1d-cbaa-806c-a5b9-000b40f6348b", "team": "기술영업팀"},
    {"id": "366cbb1d-cbaa-8066-bde5-000bbc28496e", "team": "설비기술팀"},
    {"id": "366cbb1d-cbaa-80b7-98ba-000bbd1f329c", "team": "한국생산팀"},
    {"id": "366cbb1d-cbaa-8097-91ac-000baf3183db", "team": "대구가공생산팀"},
    {"id": "366cbb1d-cbaa-806a-921b-000b65089f3d", "team": "대구품질경영팀"},
    {"id": "366cbb1d-cbaa-80fe-b40e-000b174d2241", "team": "소재개발팀"},
    {"id": "366cbb1d-cbaa-8079-ab31-000beb064b25", "team": "소재생기팀"},
    {"id": "366cbb1d-cbaa-8014-90ef-000b873a85d3", "team": "전장품질혁신팀"},
    {"id": "366cbb1d-cbaa-80a7-9c9e-000b9208d459", "team": "전장부품생산팀"},
    {"id": "366cbb1d-cbaa-8024-96a5-000bfde68d97", "team": "품질관리팀"},
    {"id": "366cbb1d-cbaa-8084-a4dc-000b002642cb", "team": "연구기획팀"},
    {"id": "366cbb1d-cbaa-805f-9e9d-000b02ebc30a", "team": "품질혁신 2팀"},
    {"id": "366cbb1d-cbaa-806c-8e59-000b5c4b3699", "team": "전장영업관리팀"},
    {"id": "366cbb1d-cbaa-80cb-a8b5-000b1f9f82eb", "team": "D LAB팀"},
    {"id": "366cbb1d-cbaa-8092-9351-000b08ccbc33", "team": "선행개발팀"},
    {"id": "366cbb1d-cbaa-80d9-b7c6-000b83aa65d6", "team": "구매팀"},
    {"id": "366cbb1d-cbaa-8040-883c-000b00aec6a3", "team": "시스템개발팀"},
    {"id": "366cbb1d-cbaa-80c2-84fd-000b9fbdef8a", "team": "기구부품생산팀"},
    {"id": "366cbb1d-cbaa-80c4-bcc1-000b0b470912", "team": "품질혁신 1팀"},
    {"id": "366cbb1d-cbaa-8080-a05c-000bfa1e8569", "team": "가공생기팀"},
    {"id": "366cbb1d-cbaa-808a-b8cc-000b2d46237b", "team": "R&D팀"},
    {"id": "366cbb1d-cbaa-8010-8350-000b11a95273", "team": "서산가공생산팀"},
    {"id": "366cbb1d-cbaa-80e8-8d51-000b4f839067", "team": "대구관리지원팀"},
    {"id": "366cbb1d-cbaa-808c-90eb-000b1b13d8a9", "team": "주조생산팀"},
    {"id": "366cbb1d-cbaa-8033-8e23-000b4cc9b46b", "team": "재경팀"},
    {"id": "5812efd1-adb1-4d63-99b0-e9b8624da86a", "team": "생산관리팀"},
    {"id": "330cbb1d-cbaa-80ce-8f8e-000be0dcc297", "team": "사업관리팀"},
    {"id": "366cbb1d-cbaa-807a-893c-000b351ef000", "team": "경영정보팀"},
    {"id": "359cbb1d-cbaa-82b2-b19a-07938394404e", "team": "선행기술팀"},
]


notion = Client(auth=TOKEN)


# =========================================================
# 공통 함수
# =========================================================

def is_object_not_found_error(e):
    code = str(getattr(e, "code", "")).lower()
    status = getattr(e, "status", None)
    msg = str(e).lower()

    return (
        "object_not_found" in code
        or "objectnotfound" in code
        or status == 404
        or "could not find database" in msg
        or "could not find data source" in msg
        or "404 not found" in msg
    )


def notion_call(func, *args, retries=5, delay=3, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)

        except APIResponseError as e:
            if is_object_not_found_error(e):
                raise

            status = getattr(e, "status", None)
            msg = str(e)

            if status == 429 or "rate_limited" in msg.lower():
                time.sleep(delay)
                continue

            if status in [500, 502, 503, 504]:
                time.sleep(delay)
                continue

            raise

        except Exception:
            if attempt < retries:
                time.sleep(delay)
                continue
            raise


def first_existing_property_name(schema, candidates):
    for name in candidates:
        if name in schema:
            return name
    return None


def find_title_property_name(schema):
    for name, prop in schema.items():
        if prop.get("type") == "title":
            return name
    return None


def plain_text_from_text_array(items):
    if not items:
        return ""
    return "".join(item.get("plain_text", "") for item in items).strip()


def make_text_array(text):
    text = "" if text is None else str(text)

    if len(text) > 2000:
        text = text[:2000]

    return [
        {
            "text": {
                "content": text
            }
        }
    ]


def get_page_title(page):
    props = page.get("properties", {})

    for _, prop_value in props.items():
        if prop_value.get("type") == "title":
            title = plain_text_from_text_array(prop_value.get("title", []))
            return title if title else "제목 없음"

    return "제목 없음"


def get_rich_text_value(prop):
    if not prop:
        return ""

    prop_type = prop.get("type")

    if prop_type == "rich_text":
        return plain_text_from_text_array(prop.get("rich_text", []))

    if prop_type == "title":
        return plain_text_from_text_array(prop.get("title", []))

    return ""


# =========================================================
# Data source 조회
# =========================================================

def retrieve_data_source(data_source_id):
    return notion_call(
        notion.data_sources.retrieve,
        data_source_id=data_source_id
    )


def get_data_source_schema(data_source_id):
    data_source = retrieve_data_source(data_source_id)
    return data_source.get("properties", {})


def get_all_pages(data_source_id):
    pages = []
    start_cursor = None

    while True:
        kwargs = {
            "data_source_id": data_source_id,
            "page_size": 100,
        }

        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        result = notion_call(notion.data_sources.query, **kwargs)

        pages.extend(result.get("results", []))

        if not result.get("has_more"):
            break

        start_cursor = result.get("next_cursor")

    if TEST_LIMIT_PER_DB is not None:
        return pages[:TEST_LIMIT_PER_DB]

    return pages


# =========================================================
# 속성 변환
# =========================================================

def property_to_plain_text(prop):
    if not prop:
        return ""

    prop_type = prop.get("type")

    if prop_type == "title":
        return plain_text_from_text_array(prop.get("title", []))

    if prop_type == "rich_text":
        return plain_text_from_text_array(prop.get("rich_text", []))

    if prop_type == "select":
        value = prop.get("select")
        return value.get("name", "") if value else ""

    if prop_type == "status":
        value = prop.get("status")
        return value.get("name", "") if value else ""

    if prop_type == "multi_select":
        return ", ".join(
            item.get("name", "")
            for item in prop.get("multi_select", [])
            if item.get("name")
        )

    if prop_type == "date":
        value = prop.get("date")
        if not value:
            return ""
        start = value.get("start", "")
        end = value.get("end", "")
        return f"{start} ~ {end}" if end else start

    if prop_type == "people":
        names = []
        for person in prop.get("people", []):
            name = person.get("name")
            if name:
                names.append(name)
        return ", ".join(names)

    if prop_type == "number":
        value = prop.get("number")
        return "" if value is None else str(value)

    if prop_type == "checkbox":
        return "true" if prop.get("checkbox") else "false"

    if prop_type == "url":
        return prop.get("url") or ""

    if prop_type == "email":
        return prop.get("email") or ""

    if prop_type == "phone_number":
        return prop.get("phone_number") or ""

    return ""


def convert_property_value(source_prop, target_prop_schema):
    if not source_prop or not target_prop_schema:
        return None

    source_type = source_prop.get("type")
    target_type = target_prop_schema.get("type")

    # 업데이트 불가 / 자동 계산 속성 제외
    if target_type in [
        "formula",
        "rollup",
        "created_time",
        "created_by",
        "last_edited_time",
        "last_edited_by",
        "unique_id",
        "verification",
        "relation",
    ]:
        return None

    if target_type == "title":
        if source_type == "title":
            text = plain_text_from_text_array(source_prop.get("title", []))
        elif source_type == "rich_text":
            text = plain_text_from_text_array(source_prop.get("rich_text", []))
        else:
            text = property_to_plain_text(source_prop)

        if not text:
            text = "제목 없음"

        return {
            "title": make_text_array(text)
        }

    if target_type == "rich_text":
        text = property_to_plain_text(source_prop)
        return {
            "rich_text": make_text_array(text)
        }

    if target_type == "number":
        if source_type == "number":
            return {
                "number": source_prop.get("number")
            }
        return None

    if target_type == "select":
        name = None

        if source_type == "select" and source_prop.get("select"):
            name = source_prop["select"].get("name")
        elif source_type == "status" and source_prop.get("status"):
            name = source_prop["status"].get("name")
        else:
            text = property_to_plain_text(source_prop)
            name = text if text else None

        if not name:
            return None

        return {
            "select": {
                "name": name
            }
        }

    if target_type == "status":
        name = None

        if source_type == "status" and source_prop.get("status"):
            name = source_prop["status"].get("name")
        elif source_type == "select" and source_prop.get("select"):
            name = source_prop["select"].get("name")

        if not name:
            return None

        return {
            "status": {
                "name": name
            }
        }

    if target_type == "multi_select":
        if source_type == "multi_select":
            values = source_prop.get("multi_select", [])
            return {
                "multi_select": [
                    {"name": item["name"]}
                    for item in values
                    if item.get("name")
                ]
            }

        if source_type == "select" and source_prop.get("select"):
            return {
                "multi_select": [
                    {"name": source_prop["select"]["name"]}
                ]
            }

        return None

    if target_type == "date":
        if source_type == "date":
            return {
                "date": source_prop.get("date")
            }
        return None

    if target_type == "people":
        if source_type == "people":
            return {
                "people": [
                    {"id": person["id"]}
                    for person in source_prop.get("people", [])
                    if person.get("id")
                ]
            }
        return None

    if target_type == "checkbox":
        if source_type == "checkbox":
            return {
                "checkbox": bool(source_prop.get("checkbox"))
            }
        return None

    if target_type == "url":
        if source_type == "url":
            return {
                "url": source_prop.get("url")
            }

        text = property_to_plain_text(source_prop)
        if text.startswith("http://") or text.startswith("https://"):
            return {
                "url": text
            }

        return None

    if target_type == "email":
        if source_type == "email":
            return {
                "email": source_prop.get("email")
            }
        return None

    if target_type == "phone_number":
        if source_type == "phone_number":
            return {
                "phone_number": source_prop.get("phone_number")
            }
        return None

    if target_type == "files":
        if source_type == "files":
            return {
                "files": source_prop.get("files", [])
            }
        return None

    return None


def set_text_like_property(target_props, target_schema, prop_name, text):
    if not prop_name:
        return

    prop_type = target_schema[prop_name].get("type")

    if prop_type == "rich_text":
        target_props[prop_name] = {
            "rich_text": make_text_array(text)
        }

    elif prop_type == "title":
        target_props[prop_name] = {
            "title": make_text_array(text)
        }

    elif prop_type == "select":
        target_props[prop_name] = {
            "select": {
                "name": text
            }
        }

    elif prop_type == "url":
        target_props[prop_name] = {
            "url": text
        }


def build_integrated_properties(
    source_page,
    target_schema,
    source_db_id,
    source_db_name
):
    source_props = source_page.get("properties", {})
    target_props = {}

    source_page_id = source_page.get("id", "")
    source_page_url = source_page.get("url", "")

    # 1. 통합 DB 제목 컬럼 채우기
    target_title_name = find_title_property_name(target_schema)

    if target_title_name:
        source_title = get_page_title(source_page)
        target_props[target_title_name] = {
            "title": make_text_array(source_title)
        }

    # 2. 같은 이름의 컬럼 자동 복사
    for prop_name, target_prop_schema in target_schema.items():
        if prop_name in EXCLUDED_PROPERTIES:
            continue

        if target_title_name and prop_name == target_title_name:
            continue

        if prop_name not in source_props:
            continue

        converted = convert_property_value(
            source_props.get(prop_name),
            target_prop_schema
        )

        if converted is not None:
            target_props[prop_name] = converted

    # 3. 원본 page ID 저장
    source_page_id_prop = first_existing_property_name(
        target_schema,
        SOURCE_PAGE_ID_PROP_CANDIDATES
    )
    set_text_like_property(
        target_props,
        target_schema,
        source_page_id_prop,
        source_page_id
    )

    # 4. 원본 DB ID 저장
    source_db_id_prop = first_existing_property_name(
        target_schema,
        SOURCE_DB_ID_PROP_CANDIDATES
    )
    set_text_like_property(
        target_props,
        target_schema,
        source_db_id_prop,
        source_db_id
    )

    # 5. 팀명 / 원본 DB명 저장
    source_db_name_prop = first_existing_property_name(
        target_schema,
        SOURCE_DB_NAME_PROP_CANDIDATES
    )
    set_text_like_property(
        target_props,
        target_schema,
        source_db_name_prop,
        source_db_name
    )

    # 6. 원본 링크 저장
    source_url_prop = first_existing_property_name(
        target_schema,
        SOURCE_URL_PROP_CANDIDATES
    )

    if source_url_prop and source_page_url:
        prop_type = target_schema[source_url_prop].get("type")

        if prop_type == "url":
            target_props[source_url_prop] = {
                "url": source_page_url
            }

        elif prop_type == "rich_text":
            target_props[source_url_prop] = {
                "rich_text": make_text_array(source_page_url)
            }

    return target_props


# =========================================================
# 변경 여부 비교
# =========================================================

def desired_text_value(desired, key):
    return plain_text_from_text_array(desired.get(key, []))


def actual_text_value(actual, key):
    return plain_text_from_text_array(actual.get(key, []))


def normalize_actual_property(actual_prop, prop_type):
    if not actual_prop:
        return None

    if prop_type == "title":
        return actual_text_value(actual_prop, "title")

    if prop_type == "rich_text":
        return actual_text_value(actual_prop, "rich_text")

    if prop_type == "number":
        return actual_prop.get("number")

    if prop_type == "select":
        value = actual_prop.get("select")
        return value.get("name") if value else None

    if prop_type == "status":
        value = actual_prop.get("status")
        return value.get("name") if value else None

    if prop_type == "multi_select":
        return sorted(
            item.get("name")
            for item in actual_prop.get("multi_select", [])
            if item.get("name")
        )

    if prop_type == "date":
        return actual_prop.get("date")

    if prop_type == "people":
        return sorted(
            person.get("id")
            for person in actual_prop.get("people", [])
            if person.get("id")
        )

    if prop_type == "checkbox":
        return bool(actual_prop.get("checkbox"))

    if prop_type == "url":
        return actual_prop.get("url")

    if prop_type == "email":
        return actual_prop.get("email")

    if prop_type == "phone_number":
        return actual_prop.get("phone_number")

    if prop_type == "files":
        files = actual_prop.get("files", [])
        return [
            {
                "name": item.get("name"),
                "type": item.get("type"),
                "external": item.get("external", {}).get("url") if item.get("type") == "external" else None,
            }
            for item in files
        ]

    return None


def normalize_desired_property(desired_prop, prop_type):
    if not desired_prop:
        return None

    if prop_type == "title":
        return desired_text_value(desired_prop, "title")

    if prop_type == "rich_text":
        return desired_text_value(desired_prop, "rich_text")

    if prop_type == "number":
        return desired_prop.get("number")

    if prop_type == "select":
        value = desired_prop.get("select")
        return value.get("name") if value else None

    if prop_type == "status":
        value = desired_prop.get("status")
        return value.get("name") if value else None

    if prop_type == "multi_select":
        return sorted(
            item.get("name")
            for item in desired_prop.get("multi_select", [])
            if item.get("name")
        )

    if prop_type == "date":
        return desired_prop.get("date")

    if prop_type == "people":
        return sorted(
            person.get("id")
            for person in desired_prop.get("people", [])
            if person.get("id")
        )

    if prop_type == "checkbox":
        return bool(desired_prop.get("checkbox"))

    if prop_type == "url":
        return desired_prop.get("url")

    if prop_type == "email":
        return desired_prop.get("email")

    if prop_type == "phone_number":
        return desired_prop.get("phone_number")

    if prop_type == "files":
        files = desired_prop.get("files", [])
        return [
            {
                "name": item.get("name"),
                "type": item.get("type"),
                "external": item.get("external", {}).get("url") if item.get("type") == "external" else None,
            }
            for item in files
        ]

    return None


def properties_changed(existing_page, desired_props, target_schema):
    """
    기존 통합 페이지와 새로 만들 속성을 비교.
    변경된 속성이 하나라도 있으면 True.
    """
    existing_props = existing_page.get("properties", {})

    for prop_name, desired_prop in desired_props.items():
        if prop_name not in target_schema:
            continue

        prop_type = target_schema[prop_name].get("type")

        actual_prop = existing_props.get(prop_name)

        actual_value = normalize_actual_property(actual_prop, prop_type)
        desired_value = normalize_desired_property(desired_prop, prop_type)

        if actual_value != desired_value:
            return True

    return False


# =========================================================
# 통합 DB 기존 데이터 조회
# =========================================================

def get_existing_target_pages(target_schema):
    source_page_id_prop = first_existing_property_name(
        target_schema,
        SOURCE_PAGE_ID_PROP_CANDIDATES
    )

    if not source_page_id_prop:
        raise RuntimeError(
            "통합 DB에 '원본 page ID' Rich text 컬럼이 없습니다. "
            "중복 방지를 위해 반드시 생성해야 합니다."
        )

    existing = {}
    start_cursor = None

    while True:
        kwargs = {
            "data_source_id": TARGET_DB_ID,
            "page_size": 100,
        }

        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        result = notion_call(notion.data_sources.query, **kwargs)

        for page in result.get("results", []):
            props = page.get("properties", {})
            prop = props.get(source_page_id_prop)

            source_page_id = get_rich_text_value(prop)

            if source_page_id:
                existing[source_page_id] = {
                    "page_id": page["id"],
                    "properties": props,
                }

        if not result.get("has_more"):
            break

        start_cursor = result.get("next_cursor")

    return existing


# =========================================================
# 통합 DB 생성 / 수정
# =========================================================

def create_target_page(properties):
    return notion_call(
        notion.pages.create,
        parent={
            "type": "data_source_id",
            "data_source_id": TARGET_DB_ID,
        },
        properties=properties
    )


def update_target_page(page_id, properties):
    return notion_call(
        notion.pages.update,
        page_id=page_id,
        properties=properties
    )


# =========================================================
# 결과표 출력
# =========================================================

def print_result_table(rows):
    print("======================================================")
    print("NO |  개수 |  추가 |  수정 | 건너뜀 |  삭제 |   팀명")
    print("------------------------------------------------------")

    total_count = 0
    total_added = 0
    total_updated = 0
    total_skipped = 0
    total_deleted = 0

    for idx, row in enumerate(rows, start=1):
        count = row.get("count", 0)
        added = row.get("added", 0)
        updated = row.get("updated", 0)
        skipped = row.get("skipped", 0)
        deleted = row.get("deleted", 0)
        team = row.get("team", "")

        total_count += count
        total_added += added
        total_updated += updated
        total_skipped += skipped
        total_deleted += deleted

        print(
            f"{idx:02d} | "
            f"{count:04d} | "
            f"{added:03d} | "
            f"{updated:03d} | "
            f"{skipped:03d} | "
            f"{deleted:03d} |   "
            f"{team}"
        )

    print("------------------------------------------------------")
    print(
        f"계 | "
        f"{total_count:04d} | "
        f"{total_added:03d} | "
        f"{total_updated:03d} | "
        f"{total_skipped:03d} | "
        f"{total_deleted:03d} |"
    )
    print("======================================================")


# =========================================================
# 메인 실행
# =========================================================

def main():
    target_schema = get_data_source_schema(TARGET_DB_ID)
    existing_target_pages = get_existing_target_pages(target_schema)

    result_rows = []

    for source in SOURCE_DBS:
        source_db_id = source.get("id", "").strip()
        team_name = source.get("team", "").strip()

        if not source_db_id:
            continue

        row = {
            "team": team_name,
            "count": 0,
            "added": 0,
            "updated": 0,
            "skipped": 0,
            "deleted": 0,
        }

        try:
            source_pages = get_all_pages(source_db_id)

        except APIResponseError as e:
            if is_object_not_found_error(e):
                # 삭제되었거나 공유 안 된 DB는 0건으로 표시하고 다음 DB로 넘어감
                result_rows.append(row)
                continue

            raise

        row["count"] = len(source_pages)

        for source_page in source_pages:
            source_page_id = source_page.get("id")

            if not source_page_id:
                row["skipped"] += 1
                continue

            try:
                desired_props = build_integrated_properties(
                    source_page=source_page,
                    target_schema=target_schema,
                    source_db_id=source_db_id,
                    source_db_name=team_name,
                )

                if not desired_props:
                    row["skipped"] += 1
                    continue

                if source_page_id in existing_target_pages:
                    existing = existing_target_pages[source_page_id]

                    if properties_changed(
                        existing_page=existing,
                        desired_props=desired_props,
                        target_schema=target_schema
                    ):
                        update_target_page(
                            page_id=existing["page_id"],
                            properties=desired_props
                        )

                        # 업데이트 후 메모리상 기존 값도 갱신
                        existing_target_pages[source_page_id]["properties"].update(
                            desired_props
                        )

                        row["updated"] += 1

                    else:
                        row["skipped"] += 1

                else:
                    created = create_target_page(desired_props)

                    existing_target_pages[source_page_id] = {
                        "page_id": created["id"],
                        "properties": desired_props,
                    }

                    row["added"] += 1

            except Exception:
                row["skipped"] += 1
                continue

        result_rows.append(row)

    print_result_table(result_rows)


if __name__ == "__main__":
    main()
