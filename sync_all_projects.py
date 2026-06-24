import os
import time
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from notion_client import Client
from notion_client.errors import APIResponseError


# =========================================================
# 로그 설정
# =========================================================

logging.getLogger("notion_client").setLevel(logging.ERROR)


# =========================================================
# 기본 설정
# =========================================================

TOKEN = os.environ["NOTION_TOKEN"]

# 통합 프로젝트 Data Source ID
TARGET_DATA_SOURCE_ID = "395cbb1d-cbaa-829c-a5a4-878f6a7b9b7d"

# 실행 결과 저장 Data Source ID
RESULT_DATA_SOURCE_ID = "389cbb1d-cbaa-801b-9855-000b71234b6f"

# 테스트할 때만 숫자 입력. 전체 실행은 None.
TEST_LIMIT_PER_DB = None

# Notion API 과호출 방지
API_SLEEP_SEC = 0.05

KST = ZoneInfo("Asia/Seoul")

notion = Client(auth=TOKEN)


# =========================================================
# 제외 / 후보 속성
# =========================================================

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

LAST_EDITED_TIME_PROP_CANDIDATES = [
    "최종 편집 일시",
    "최종 편집일시",
    "최종 수정 일시",
    "최종수정일시",
    "last_edited_time",
    "Last Edited Time",
]


# =========================================================
# 원본 Data Source 목록
# =========================================================

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
    {"id": "366cbb1d-cbaa-8084-a4dc-000b002642cb", "team": "연구기획팀"},
    {"id": "366cbb1d-cbaa-806c-8e59-000b5c4b3699", "team": "전장영업관리팀"},
    {"id": "366cbb1d-cbaa-80cb-a8b5-000b1f9f82eb", "team": "D LAB팀"},
    {"id": "366cbb1d-cbaa-8092-9351-000b08ccbc33", "team": "선행개발팀"},
    {"id": "366cbb1d-cbaa-80d9-b7c6-000b83aa65d6", "team": "구매팀"},
    {"id": "366cbb1d-cbaa-8040-883c-000b00aec6a3", "team": "시스템개발팀"},
    {"id": "366cbb1d-cbaa-80c2-84fd-000b9fbdef8a", "team": "기구부품생산팀"},
    {"id": "366cbb1d-cbaa-80c4-bcc1-000b0b470912", "team": "품질혁신실"},
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


# =========================================================
# 공통 함수
# =========================================================

def sleep_api():
    time.sleep(API_SLEEP_SEC)


def now_kst():
    return datetime.now(KST)


def today_kst_date():
    return now_kst().date().isoformat()


def safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def is_object_not_found_error(error):
    try:
        return error.code == "object_not_found"
    except Exception:
        return False


def get_first_existing_prop_name(schema, candidates):
    for name in candidates:
        if name in schema:
            return name
    return None


def get_title_property_name(schema):
    for name, info in schema.items():
        if info.get("type") == "title":
            return name
    return None


def get_latest_edited_time_from_pages(pages):
    latest_edited_time = None

    for page in pages:
        page_last_edited_time = page.get("last_edited_time")

        if not page_last_edited_time:
            continue

        if latest_edited_time is None or page_last_edited_time > latest_edited_time:
            latest_edited_time = page_last_edited_time

    return latest_edited_time


# =========================================================
# Data Source 조회 함수
# =========================================================

def retrieve_data_source_schema(data_source_id):
    sleep_api()

    if hasattr(notion, "data_sources"):
        ds = notion.data_sources.retrieve(data_source_id=data_source_id)
        return ds.get("properties", {})

    db = notion.databases.retrieve(database_id=data_source_id)
    return db.get("properties", {})


def query_all_pages(data_source_id):
    results = []
    start_cursor = None

    while True:
        if hasattr(notion, "data_sources"):
            payload = {
                "data_source_id": data_source_id,
                "page_size": 100,
            }

            if start_cursor:
                payload["start_cursor"] = start_cursor

            sleep_api()
            response = notion.data_sources.query(**payload)

        else:
            payload = {
                "database_id": data_source_id,
                "page_size": 100,
            }

            if start_cursor:
                payload["start_cursor"] = start_cursor

            sleep_api()
            response = notion.databases.query(**payload)

        results.extend(response.get("results", []))

        if TEST_LIMIT_PER_DB is not None and len(results) >= TEST_LIMIT_PER_DB:
            return results[:TEST_LIMIT_PER_DB]

        if not response.get("has_more"):
            break

        start_cursor = response.get("next_cursor")

    return results


# =========================================================
# 속성 값 추출 함수
# =========================================================

def plain_text_from_title(prop):
    title = prop.get("title", []) if prop else []
    return "".join(item.get("plain_text", "") for item in title)


def plain_text_from_rich_text(prop):
    rich_text = prop.get("rich_text", []) if prop else []
    return "".join(item.get("plain_text", "") for item in rich_text)


def get_prop_plain_value(prop):
    if not prop:
        return None

    prop_type = prop.get("type")

    if prop_type == "title":
        return plain_text_from_title(prop)

    if prop_type == "rich_text":
        return plain_text_from_rich_text(prop)

    if prop_type == "number":
        return prop.get("number")

    if prop_type == "select":
        value = prop.get("select")
        return value.get("name") if value else None

    if prop_type == "multi_select":
        return [item.get("name") for item in prop.get("multi_select", [])]

    if prop_type == "status":
        value = prop.get("status")
        return value.get("name") if value else None

    if prop_type == "date":
        value = prop.get("date")
        return value.get("start") if value else None

    if prop_type == "checkbox":
        return prop.get("checkbox")

    if prop_type == "url":
        return prop.get("url")

    if prop_type == "email":
        return prop.get("email")

    if prop_type == "phone_number":
        return prop.get("phone_number")

    if prop_type == "people":
        return [person.get("id") for person in prop.get("people", [])]

    if prop_type == "files":
        return [file.get("name") for file in prop.get("files", [])]

    return None


# =========================================================
# 속성 변환 함수
# =========================================================

def convert_property_for_update(source_prop, target_prop_type):
    if not source_prop:
        return None

    source_type = source_prop.get("type")

    if source_type == "title" and target_prop_type == "title":
        text = plain_text_from_title(source_prop)
        return {
            "title": [
                {
                    "text": {
                        "content": text
                    }
                }
            ]
        }

    if source_type == "rich_text" and target_prop_type == "rich_text":
        text = plain_text_from_rich_text(source_prop)
        return {
            "rich_text": [
                {
                    "text": {
                        "content": text
                    }
                }
            ]
        }

    if source_type == "number" and target_prop_type == "number":
        return {
            "number": source_prop.get("number")
        }

    if source_type == "select" and target_prop_type == "select":
        value = source_prop.get("select")
        if value:
            return {
                "select": {
                    "name": value.get("name")
                }
            }
        return {"select": None}

    if source_type == "multi_select" and target_prop_type == "multi_select":
        return {
            "multi_select": [
                {
                    "name": item.get("name")
                }
                for item in source_prop.get("multi_select", [])
                if item.get("name")
            ]
        }

    if source_type == "status" and target_prop_type == "status":
        value = source_prop.get("status")
        if value:
            return {
                "status": {
                    "name": value.get("name")
                }
            }
        return {"status": None}

    if source_type == "date" and target_prop_type == "date":
        return {
            "date": source_prop.get("date")
        }

    if source_type == "checkbox" and target_prop_type == "checkbox":
        return {
            "checkbox": bool(source_prop.get("checkbox"))
        }

    if source_type == "url" and target_prop_type == "url":
        return {
            "url": source_prop.get("url")
        }

    if source_type == "email" and target_prop_type == "email":
        return {
            "email": source_prop.get("email")
        }

    if source_type == "phone_number" and target_prop_type == "phone_number":
        return {
            "phone_number": source_prop.get("phone_number")
        }

    if source_type == "people" and target_prop_type == "people":
        return {
            "people": [
                {
                    "id": person.get("id")
                }
                for person in source_prop.get("people", [])
                if person.get("id")
            ]
        }

    if source_type == "files" and target_prop_type == "files":
        files = []

        for file in source_prop.get("files", []):
            file_type = file.get("type")
            name = file.get("name")

            if file_type == "external":
                url = file.get("external", {}).get("url")
                if url:
                    files.append({
                        "name": name,
                        "external": {
                            "url": url
                        }
                    })

        return {
            "files": files
        }

    return None


def make_text_property(value, target_prop_type):
    value = "" if value is None else str(value)

    if target_prop_type == "rich_text":
        return {
            "rich_text": [
                {
                    "text": {
                        "content": value
                    }
                }
            ]
        }

    if target_prop_type == "title":
        return {
            "title": [
                {
                    "text": {
                        "content": value
                    }
                }
            ]
        }

    if target_prop_type == "url":
        return {
            "url": value
        }

    if target_prop_type == "select":
        return {
            "select": {
                "name": value
            }
        }

    return None


# =========================================================
# 통합 DB 속성 생성
# =========================================================

def build_integrated_properties(
    source_page,
    target_schema,
    source_data_source_id,
    source_data_source_name,
):
    source_props = source_page.get("properties", {})
    source_page_id = source_page.get("id")
    source_url = source_page.get("url")
    source_last_edited_time = source_page.get("last_edited_time")

    desired_props = {}

    target_title_prop_name = get_title_property_name(target_schema)
    source_title_prop_name = get_title_property_name(source_props)

    # 1) 제목 속성
    if target_title_prop_name and source_title_prop_name:
        source_title_prop = source_props.get(source_title_prop_name)
        title_text = plain_text_from_title(source_title_prop) or "제목 없음"

        desired_props[target_title_prop_name] = {
            "title": [
                {
                    "text": {
                        "content": title_text
                    }
                }
            ]
        }

    # 2) 같은 이름 / 같은 타입 속성 복사
    for prop_name, source_prop in source_props.items():
        if prop_name in EXCLUDED_PROPERTIES:
            continue

        if prop_name not in target_schema:
            continue

        target_prop_type = target_schema[prop_name].get("type")

        if target_prop_type == "title":
            continue

        if target_prop_type in {
            "formula",
            "rollup",
            "created_time",
            "created_by",
            "last_edited_time",
            "last_edited_by",
            "unique_id",
            "button",
        }:
            continue

        converted = convert_property_for_update(source_prop, target_prop_type)

        if converted is not None:
            desired_props[prop_name] = converted

    # 3) 원본 page ID
    source_page_id_prop_name = get_first_existing_prop_name(
        target_schema,
        SOURCE_PAGE_ID_PROP_CANDIDATES
    )

    if source_page_id_prop_name:
        target_type = target_schema[source_page_id_prop_name].get("type")
        prop = make_text_property(source_page_id, target_type)

        if prop:
            desired_props[source_page_id_prop_name] = prop

    # 4) 원본 Data Source ID
    source_db_id_prop_name = get_first_existing_prop_name(
        target_schema,
        SOURCE_DB_ID_PROP_CANDIDATES
    )

    if source_db_id_prop_name:
        target_type = target_schema[source_db_id_prop_name].get("type")
        prop = make_text_property(source_data_source_id, target_type)

        if prop:
            desired_props[source_db_id_prop_name] = prop

    # 5) 원본 URL
    source_url_prop_name = get_first_existing_prop_name(
        target_schema,
        SOURCE_URL_PROP_CANDIDATES
    )

    if source_url_prop_name:
        target_type = target_schema[source_url_prop_name].get("type")
        prop = make_text_property(source_url, target_type)

        if prop:
            desired_props[source_url_prop_name] = prop

    # 6) 팀명 / 원본 DB명
    source_db_name_prop_name = get_first_existing_prop_name(
        target_schema,
        SOURCE_DB_NAME_PROP_CANDIDATES
    )

    if source_db_name_prop_name:
        target_type = target_schema[source_db_name_prop_name].get("type")
        prop = make_text_property(source_data_source_name, target_type)

        if prop:
            desired_props[source_db_name_prop_name] = prop

    # 7) 원본 페이지의 최종 편집 일시를 통합 DB의 Date 속성에 저장
    last_edited_time_prop_name = get_first_existing_prop_name(
        target_schema,
        LAST_EDITED_TIME_PROP_CANDIDATES
    )

    if last_edited_time_prop_name:
        target_type = target_schema[last_edited_time_prop_name].get("type")

        if target_type == "date" and source_last_edited_time:
            desired_props[last_edited_time_prop_name] = {
                "date": {
                    "start": source_last_edited_time
                }
            }

    return desired_props


# =========================================================
# 통합 DB 기존 페이지 매핑
# =========================================================

def get_existing_target_pages(target_schema):
    pages = query_all_pages(TARGET_DATA_SOURCE_ID)
    existing = {}

    source_page_id_prop_name = get_first_existing_prop_name(
        target_schema,
        SOURCE_PAGE_ID_PROP_CANDIDATES
    )

    if not source_page_id_prop_name:
        raise ValueError(
            "통합 DB에 원본 페이지 ID 속성이 없습니다. "
            "예: '원본 페이지 ID' 속성을 만들어야 중복 생성 없이 업데이트가 가능합니다."
        )

    for page in pages:
        props = page.get("properties", {})
        source_page_id = get_prop_plain_value(props.get(source_page_id_prop_name))

        if source_page_id:
            existing[source_page_id] = {
                "page_id": page.get("id"),
                "properties": props,
            }

    return existing


# =========================================================
# 속성 비교
# =========================================================

def normalize_desired_property(prop):
    if not prop:
        return None

    if "title" in prop:
        return "".join(
            item.get("text", {}).get("content", "")
            for item in prop.get("title", [])
        )

    if "rich_text" in prop:
        return "".join(
            item.get("text", {}).get("content", "")
            for item in prop.get("rich_text", [])
        )

    if "number" in prop:
        return prop.get("number")

    if "select" in prop:
        value = prop.get("select")
        return value.get("name") if value else None

    if "multi_select" in prop:
        return [item.get("name") for item in prop.get("multi_select", [])]

    if "status" in prop:
        value = prop.get("status")
        return value.get("name") if value else None

    if "date" in prop:
        value = prop.get("date")
        return value.get("start") if value else None

    if "checkbox" in prop:
        return prop.get("checkbox")

    if "url" in prop:
        return prop.get("url")

    if "email" in prop:
        return prop.get("email")

    if "phone_number" in prop:
        return prop.get("phone_number")

    if "people" in prop:
        return [person.get("id") for person in prop.get("people", [])]

    if "files" in prop:
        return [file.get("name") for file in prop.get("files", [])]

    return prop


def properties_changed(existing_page, desired_props):
    existing_props = existing_page.get("properties", {})

    for prop_name, desired_prop in desired_props.items():
        existing_prop = existing_props.get(prop_name)

        existing_value = get_prop_plain_value(existing_prop)
        desired_value = normalize_desired_property(desired_prop)

        if existing_value != desired_value:
            return True

    return False


# =========================================================
# 페이지 생성 / 수정 / 삭제
# =========================================================

def create_page_in_data_source(data_source_id, properties):
    sleep_api()

    try:
        return notion.pages.create(
            parent={
                "data_source_id": data_source_id
            },
            properties=properties,
        )
    except Exception:
        return notion.pages.create(
            parent={
                "database_id": data_source_id
            },
            properties=properties,
        )


def create_target_page(properties):
    return create_page_in_data_source(
        TARGET_DATA_SOURCE_ID,
        properties,
    )


def update_target_page(page_id, properties):
    sleep_api()
    return notion.pages.update(
        page_id=page_id,
        properties=properties,
    )


def archive_page(page_id):
    sleep_api()
    return notion.pages.update(
        page_id=page_id,
        archived=True,
    )


# =========================================================
# 결과 DB 초기화 후 저장
# =========================================================

def clear_result_data_source():
    """
    결과 DB에 기존 생성되어 있던 페이지를 전부 휴지통 처리.
    Notion API는 완전 삭제가 아니라 archived=True 방식으로 처리함.
    """

    print("[INFO] 결과 DB 기존 페이지 삭제 시작")

    pages = query_all_pages(RESULT_DATA_SOURCE_ID)

    deleted_count = 0

    for page in pages:
        page_id = page.get("id")

        if not page_id:
            continue

        try:
            archive_page(page_id)
            deleted_count += 1
        except Exception as e:
            print(f"[WARN] 결과 DB 기존 페이지 삭제 실패: {page_id} / {e}")
            continue

    print(f"[INFO] 결과 DB 기존 페이지 삭제 완료: {deleted_count}건")


def build_result_properties(row):
    props = {
        "No": {
            "number": safe_int(row.get("no"))
        },
        "날짜": {
            "date": {
                "start": today_kst_date()
            }
        },
        "팀명": {
            "title": [
                {
                    "text": {
                        "content": str(row.get("team_name") or "")
                    }
                }
            ]
        },
        "프로젝트 수": {
            "number": safe_int(row.get("count"))
        },
        "추가": {
            "number": safe_int(row.get("added"))
        },
        "수정": {
            "number": safe_int(row.get("updated"))
        },
        "건너뜀": {
            "number": safe_int(row.get("skipped"))
        },
        "삭제": {
            "number": safe_int(row.get("deleted"))
        },
    }

    latest_edited_time = row.get("latest_edited_time")

    if latest_edited_time:
        props["최종 편집 일시"] = {
            "date": {
                "start": latest_edited_time
            }
        }

    return props


def create_result_page(row):
    return create_page_in_data_source(
        RESULT_DATA_SOURCE_ID,
        build_result_properties(row),
    )


def save_result_rows_to_notion(result_rows):
    """
    결과 DB를 먼저 비우고, 이번 실행 결과만 새로 생성.
    """

    clear_result_data_source()

    print("[INFO] 결과 DB 신규 페이지 생성 시작")

    created_count = 0

    for index, row in enumerate(result_rows, start=1):
        row["no"] = index

        try:
            create_result_page(row)
            created_count += 1
        except Exception as e:
            print(f"[WARN] 결과 DB 저장 실패: {row.get('team_name')} / {e}")
            continue

    print(f"[INFO] 결과 DB 신규 페이지 생성 완료: {created_count}건")


# =========================================================
# 결과 출력
# =========================================================

def print_result_table(result_rows):
    print("")
    print("======================================")
    print("프로젝트 통합 결과")
    print("======================================")
    print("No | 팀명 | 프로젝트 수 | 추가 | 수정 | 건너뜀 | 삭제 | 최신 편집 일시")
    print("--------------------------------------")

    for index, row in enumerate(result_rows, start=1):
        print(
            f"{index} | "
            f"{row.get('team_name', '')} | "
            f"{row.get('count', 0)} | "
            f"{row.get('added', 0)} | "
            f"{row.get('updated', 0)} | "
            f"{row.get('skipped', 0)} | "
            f"{row.get('deleted', 0)} | "
            f"{row.get('latest_edited_time') or ''}"
        )

    print("======================================")
    print("")


# =========================================================
# 메인
# =========================================================

def main():
    print("======================================")
    print("Notion 프로젝트 통합 시작")
    print("======================================")

    print("[INFO] 통합 Data Source schema 조회")
    target_schema = retrieve_data_source_schema(TARGET_DATA_SOURCE_ID)

    print("[INFO] 통합 DB 기존 페이지 조회")
    existing_target_pages = get_existing_target_pages(target_schema)
    print(f"[INFO] 기존 통합 페이지 수: {len(existing_target_pages)}")

    result_rows = []

    for source_db in SOURCE_DBS:
        source_data_source_id = source_db["id"]
        team_name = source_db["team"]

        row = {
            "no": 0,
            "team_name": team_name,
            "source_db_id": source_data_source_id,
            "count": 0,
            "added": 0,
            "updated": 0,
            "skipped": 0,
            "deleted": 0,
            "latest_edited_time": None,
        }

        print("--------------------------------------")
        print(f"[INFO] 원본 DB: {team_name}")
        print(f"[INFO] 원본 Data Source ID: {source_data_source_id}")

        try:
            source_pages = query_all_pages(source_data_source_id)

        except APIResponseError as e:
            if is_object_not_found_error(e):
                print(
                    f"[WARN] 접근 불가 또는 공유 안 됨: "
                    f"{team_name} / {source_data_source_id}"
                )
                result_rows.append(row)
                continue

            raise

        row["count"] = len(source_pages)
        row["latest_edited_time"] = get_latest_edited_time_from_pages(source_pages)

        print(f"[INFO] 원본 페이지 수: {row['count']}")
        print(f"[INFO] 최신 편집 일시: {row['latest_edited_time'] or ''}")

        for source_page in source_pages:
            source_page_id = source_page.get("id")

            if not source_page_id:
                row["skipped"] += 1
                continue

            try:
                desired_props = build_integrated_properties(
                    source_page=source_page,
                    target_schema=target_schema,
                    source_data_source_id=source_data_source_id,
                    source_data_source_name=team_name,
                )

                if not desired_props:
                    row["skipped"] += 1
                    continue

                if source_page_id in existing_target_pages:
                    existing = existing_target_pages[source_page_id]

                    if properties_changed(
                        existing_page=existing,
                        desired_props=desired_props,
                    ):
                        update_target_page(
                            page_id=existing["page_id"],
                            properties=desired_props,
                        )

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

            except Exception as e:
                print(
                    f"[WARN] 페이지 처리 실패: "
                    f"{team_name} / {source_page_id} / {e}"
                )
                row["skipped"] += 1
                continue

        result_rows.append(row)

    print_result_table(result_rows)

    print("[INFO] 실행 결과 Notion DB 저장 시작")
    save_result_rows_to_notion(result_rows)
    print("[INFO] 실행 결과 Notion DB 저장 완료")

    print("======================================")
    print("Notion 프로젝트 통합 완료")
    print("======================================")


if __name__ == "__main__":
    main()
