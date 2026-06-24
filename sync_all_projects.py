import os
import time
from notion_client import Client
from notion_client.errors import APIResponseError


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

# 원본 page ID를 저장할 통합 DB 컬럼명 후보
SOURCE_PAGE_ID_PROP_CANDIDATES = [
    "원본 page ID",
    "원본 Page ID",
    "원본페이지ID",
    "원본 페이지 ID",
    "source_page_id",
    "Source Page ID",
]

# 원본 DB ID를 저장할 통합 DB 컬럼명 후보
SOURCE_DB_ID_PROP_CANDIDATES = [
    "원본 DB ID",
    "원본DB ID",
    "원본 데이터소스 ID",
    "source_db_id",
    "Source DB ID",
]

# 원본 링크를 저장할 통합 DB 컬럼명 후보
SOURCE_URL_PROP_CANDIDATES = [
    "원본 링크",
    "원본링크",
    "Source URL",
    "source_url",
    "URL",
]

# 원본 DB명을 저장할 통합 DB 컬럼명 후보
SOURCE_DB_NAME_PROP_CANDIDATES = [
    "원본 DB",
    "원본DB",
    "원본 DB명",
    "source_db",
    "Source DB",
]


SOURCE_DBS = [
    {"id": "366cbb1d-cbaa-8035-925a-000b1ddd6708"},
    {"id": "366cbb1d-cbaa-8044-9bef-000bc920e796"},
    {"id": "366cbb1d-cbaa-8022-8c86-000bcbc581a5"},
    {"id": "366cbb1d-cbaa-803b-9c86-000baf05603b"},
    {"id": "366cbb1d-cbaa-80d8-a15c-000b0f1354f1"},
    {"id": "366cbb1d-cbaa-8064-b4c5-000bf7f43e67"},
    {"id": "366cbb1d-cbaa-80a4-9920-000bb0c809a5"},
    {"id": "366cbb1d-cbaa-80be-8b9d-000bd0ca2dae"},
    {"id": "366cbb1d-cbaa-8026-ab8c-000b7fc774e3"},
    {"id": "366cbb1d-cbaa-807a-97dd-000b3aca14a1"},
    {"id": "366cbb1d-cbaa-806c-a5b9-000b40f6348b"},
    {"id": "366cbb1d-cbaa-8066-bde5-000bbc28496e"},
    {"id": "366cbb1d-cbaa-80b7-98ba-000bbd1f329c"},
    {"id": "366cbb1d-cbaa-8097-91ac-000baf3183db"},
    {"id": "366cbb1d-cbaa-806a-921b-000b65089f3d"},
    {"id": "366cbb1d-cbaa-80fe-b40e-000b174d2241"},
    {"id": "366cbb1d-cbaa-8079-ab31-000beb064b25"},
    {"id": "366cbb1d-cbaa-8014-90ef-000b873a85d3"},
    {"id": "366cbb1d-cbaa-80a7-9c9e-000b9208d459"},
    {"id": "366cbb1d-cbaa-8024-96a5-000bfde68d97"},
    {"id": "366cbb1d-cbaa-8084-a4dc-000b002642cb"},
    {"id": "366cbb1d-cbaa-805f-9e9d-000b02ebc30a"},
    {"id": "366cbb1d-cbaa-806c-8e59-000b5c4b3699"},
    {"id": "366cbb1d-cbaa-80cb-a8b5-000b1f9f82eb"},
    {"id": "366cbb1d-cbaa-8092-9351-000b08ccbc33"},
    {"id": "366cbb1d-cbaa-80d9-b7c6-000b83aa65d6"},
    {"id": "366cbb1d-cbaa-8040-883c-000b00aec6a3"},
    {"id": "366cbb1d-cbaa-80c2-84fd-000b9fbdef8a"},
    {"id": "366cbb1d-cbaa-80c4-bcc1-000b0b470912"},
    {"id": "366cbb1d-cbaa-8080-a05c-000bfa1e8569"},
    {"id": "366cbb1d-cbaa-808a-b8cc-000b2d46237b"},
    {"id": "366cbb1d-cbaa-8010-8350-000b11a95273"},
    {"id": "366cbb1d-cbaa-80e8-8d51-000b4f839067"},
    {"id": "366cbb1d-cbaa-808c-90eb-000b1b13d8a9"},
    {"id": "366cbb1d-cbaa-8033-8e23-000b4cc9b46b"},
    {"id": "5812efd1-adb1-4d63-99b0-e9b8624da86a"},
    {"id": "330cbb1d-cbaa-80ce-8f8e-000be0dcc297"},
    {"id": "366cbb1d-cbaa-807a-893c-000b351ef000"},
    {"id": "359cbb1d-cbaa-82b2-b19a-07938394404e"},
]


notion = Client(auth=TOKEN)


# =========================================================
# 공통 유틸
# =========================================================

def is_object_not_found_error(e):
    """
    삭제된 DB, 공유 안 된 DB, 잘못된 ID일 때 발생하는 오류 판별.
    """
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
    """
    Notion API 공통 호출 함수.
    404/ObjectNotFound는 재시도해도 해결되지 않으므로 그대로 raise.
    나머지 일시 오류는 재시도.
    """
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)

        except APIResponseError as e:
            if is_object_not_found_error(e):
                raise

            status = getattr(e, "status", None)
            msg = str(e)

            if status == 429 or "rate_limited" in msg.lower():
                print(f"[WARN] Rate limited. retry {attempt}/{retries} after {delay} sec")
                time.sleep(delay)
                continue

            if status in [500, 502, 503, 504]:
                print(f"[WARN] Notion server error. retry {attempt}/{retries} after {delay} sec")
                time.sleep(delay)
                continue

            raise

        except Exception as e:
            msg = str(e)

            if attempt < retries:
                print(f"[WARN] request fail: {msg}, attempt={attempt}")
                time.sleep(delay)
                continue

            raise


def first_existing_property_name(schema, candidates):
    """
    schema 안에 후보 컬럼명이 있으면 첫 번째 일치 컬럼명 반환.
    """
    for name in candidates:
        if name in schema:
            return name
    return None


def find_title_property_name(schema):
    """
    Data source schema에서 title 타입 컬럼명 찾기.
    """
    for name, prop in schema.items():
        if prop.get("type") == "title":
            return name
    return None


def plain_text_from_text_array(items):
    if not items:
        return ""

    return "".join(item.get("plain_text", "") for item in items).strip()


def get_page_title(page):
    """
    페이지에서 title 타입 속성 값을 찾아 텍스트로 반환.
    """
    props = page.get("properties", {})

    for prop_name, prop_value in props.items():
        if prop_value.get("type") == "title":
            return plain_text_from_text_array(prop_value.get("title", []))

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


def get_data_source_name(data_source_id):
    try:
        data_source = retrieve_data_source(data_source_id)
        title_items = data_source.get("title", [])
        title = plain_text_from_text_array(title_items)

        if title:
            return title

    except APIResponseError as e:
        if is_object_not_found_error(e):
            raise

    return f"원본DB-{data_source_id[:8]}"


def get_all_pages(data_source_id):
    """
    Data source의 모든 페이지 조회.
    """
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
        batch = result.get("results", [])

        pages.extend(batch)

        if not result.get("has_more"):
            break

        start_cursor = result.get("next_cursor")

    if TEST_LIMIT_PER_DB is not None:
        return pages[:TEST_LIMIT_PER_DB]

    return pages


# =========================================================
# 속성 변환
# =========================================================

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


def convert_property_value(source_prop, target_prop_schema):
    """
    원본 페이지 속성을 통합 DB 속성 타입에 맞게 변환.
    Notion에서 업데이트 불가능한 타입은 None 반환.
    """
    if not source_prop or not target_prop_schema:
        return None

    source_type = source_prop.get("type")
    target_type = target_prop_schema.get("type")

    # 읽기 전용 / 자동 속성은 업데이트 불가
    if target_type in [
        "formula",
        "rollup",
        "created_time",
        "created_by",
        "last_edited_time",
        "last_edited_by",
        "unique_id",
        "verification",
    ]:
        return None

    # title
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

    # rich_text
    if target_type == "rich_text":
        text = property_to_plain_text(source_prop)
        return {
            "rich_text": make_text_array(text)
        }

    # number
    if target_type == "number":
        if source_type == "number":
            return {
                "number": source_prop.get("number")
            }
        return None

    # select
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

    # status
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

    # multi_select
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

    # date
    if target_type == "date":
        if source_type == "date":
            return {
                "date": source_prop.get("date")
            }
        return None

    # people
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

    # checkbox
    if target_type == "checkbox":
        if source_type == "checkbox":
            return {
                "checkbox": bool(source_prop.get("checkbox"))
            }
        return None

    # url
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

    # email
    if target_type == "email":
        if source_type == "email":
            return {
                "email": source_prop.get("email")
            }
        return None

    # phone_number
    if target_type == "phone_number":
        if source_type == "phone_number":
            return {
                "phone_number": source_prop.get("phone_number")
            }
        return None

    # files
    if target_type == "files":
        if source_type == "files":
            return {
                "files": source_prop.get("files", [])
            }
        return None

    # relation은 DB 관계가 다르면 오류 가능성이 커서 자동 복사 제외
    if target_type == "relation":
        return None

    return None


def property_to_plain_text(prop):
    """
    여러 타입의 Notion 속성을 사람이 읽을 수 있는 텍스트로 변환.
    """
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

    if prop_type == "created_time":
        return prop.get("created_time") or ""

    if prop_type == "last_edited_time":
        return prop.get("last_edited_time") or ""

    return ""


def build_integrated_properties(
    source_page,
    source_schema,
    target_schema,
    source_db_id,
    source_db_name
):
    """
    원본 페이지를 통합 DB 페이지 속성으로 변환.
    """
    source_props = source_page.get("properties", {})
    target_props = {}

    source_page_id = source_page.get("id", "")
    source_page_url = source_page.get("url", "")

    # 1. 통합 DB title 컬럼 채우기
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

    if source_page_id_prop:
        prop_type = target_schema[source_page_id_prop].get("type")

        if prop_type == "rich_text":
            target_props[source_page_id_prop] = {
                "rich_text": make_text_array(source_page_id)
            }
        elif prop_type == "title":
            target_props[source_page_id_prop] = {
                "title": make_text_array(source_page_id)
            }

    # 4. 원본 DB ID 저장
    source_db_id_prop = first_existing_property_name(
        target_schema,
        SOURCE_DB_ID_PROP_CANDIDATES
    )

    if source_db_id_prop:
        prop_type = target_schema[source_db_id_prop].get("type")

        if prop_type == "rich_text":
            target_props[source_db_id_prop] = {
                "rich_text": make_text_array(source_db_id)
            }
        elif prop_type == "title":
            target_props[source_db_id_prop] = {
                "title": make_text_array(source_db_id)
            }

    # 5. 원본 DB명 저장
    source_db_name_prop = first_existing_property_name(
        target_schema,
        SOURCE_DB_NAME_PROP_CANDIDATES
    )

    if source_db_name_prop:
        prop_type = target_schema[source_db_name_prop].get("type")

        if prop_type == "rich_text":
            target_props[source_db_name_prop] = {
                "rich_text": make_text_array(source_db_name)
            }
        elif prop_type == "select":
            target_props[source_db_name_prop] = {
                "select": {
                    "name": source_db_name
                }
            }
        elif prop_type == "title":
            target_props[source_db_name_prop] = {
                "title": make_text_array(source_db_name)
            }

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
# 통합 DB 기존 데이터 조회
# =========================================================

def get_existing_target_pages(target_schema):
    """
    통합 DB에서 기존 데이터를 조회해서
    원본 page ID 기준으로 dict 생성.
    """
    source_page_id_prop = first_existing_property_name(
        target_schema,
        SOURCE_PAGE_ID_PROP_CANDIDATES
    )

    if not source_page_id_prop:
        print("[WARN] 통합 DB에 '원본 page ID' 컬럼이 없습니다.")
        print("[WARN] 중복 방지를 위해 통합 DB에 '원본 page ID' Rich text 컬럼을 만드는 것을 권장합니다.")
        return {}

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
                existing[source_page_id] = page["id"]

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
# 메인 실행
# =========================================================

def main():
    print("======================================")
    print("Notion 프로젝트 통합 시작")
    print("======================================")

    print("[INFO] 통합 DB schema 조회")
    target_schema = get_data_source_schema(TARGET_DB_ID)

    print("[INFO] 통합 DB 기존 페이지 조회")
    existing_target_pages = get_existing_target_pages(target_schema)
    print(f"[INFO] 기존 통합 페이지 수: {len(existing_target_pages)}")

    total_source_db = 0
    skipped_db = 0
    total_source_pages = 0
    created_count = 0
    updated_count = 0
    failed_page_count = 0

    skipped_db_ids = []

    for source in SOURCE_DBS:
        source_db_id = source.get("id", "").strip()

        if not source_db_id:
            continue

        total_source_db += 1

        try:
            source_db_name = get_data_source_name(source_db_id)
            source_schema = get_data_source_schema(source_db_id)
            source_pages = get_all_pages(source_db_id)

        except APIResponseError as e:
            if is_object_not_found_error(e):
                skipped_db += 1
                skipped_db_ids.append(source_db_id)
                print(f"[SKIP] 삭제되었거나 공유되지 않은 DB 건너뜀: {source_db_id}")
                continue

            print(f"[ERROR] 원본 DB 조회 실패: {source_db_id} / {e}")
            raise

        except Exception as e:
            print(f"[ERROR] 원본 DB 처리 중 예외 발생: {source_db_id} / {e}")
            raise

        print("--------------------------------------")
        print(f"[INFO] 원본 DB: {source_db_name}")
        print(f"[INFO] 원본 DB ID: {source_db_id}")
        print(f"[INFO] 원본 페이지 수: {len(source_pages)}")

        for source_page in source_pages:
            source_page_id = source_page.get("id")

            if not source_page_id:
                failed_page_count += 1
                print("[WARN] page id 없는 항목 건너뜀")
                continue

            try:
                properties = build_integrated_properties(
                    source_page=source_page,
                    source_schema=source_schema,
                    target_schema=target_schema,
                    source_db_id=source_db_id,
                    source_db_name=source_db_name
                )

                if not properties:
                    failed_page_count += 1
                    print(f"[WARN] 변환된 속성이 없어 건너뜀: {source_page_id}")
                    continue

                if source_page_id in existing_target_pages:
                    target_page_id = existing_target_pages[source_page_id]
                    update_target_page(target_page_id, properties)
                    updated_count += 1

                else:
                    created = create_target_page(properties)
                    existing_target_pages[source_page_id] = created["id"]
                    created_count += 1

                total_source_pages += 1

            except APIResponseError as e:
                failed_page_count += 1
                print(f"[WARN] 페이지 취합 실패: {source_page_id} / {e}")
                continue

            except Exception as e:
                failed_page_count += 1
                print(f"[WARN] 페이지 처리 중 예외 발생: {source_page_id} / {e}")
                continue

    print("======================================")
    print("Notion 프로젝트 통합 완료")
    print("======================================")
    print(f"대상 원본 DB 수: {total_source_db}")
    print(f"건너뛴 DB 수: {skipped_db}")
    print(f"처리된 원본 페이지 수: {total_source_pages}")
    print(f"신규 생성: {created_count}")
    print(f"업데이트: {updated_count}")
    print(f"실패 페이지 수: {failed_page_count}")

    if skipped_db_ids:
        print("--------------------------------------")
        print("건너뛴 DB 목록")
        for db_id in skipped_db_ids:
            print(f"- {db_id}")

    print("======================================")


if __name__ == "__main__":
    main()
