import os
import time
from notion_client import Client

TOKEN = os.environ["NOTION_TOKEN"]

TARGET_DB_ID = "395cbb1d-cbaa-829c-a5a4-878f6a7b9b7d"

TEST_LIMIT_PER_DB = None

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


def notion_call(func, *args, retries=5, delay=3, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            msg = str(e)

            if "502" in msg or "503" in msg or "504" in msg or "Bad Gateway" in msg:
                print(f"일시 오류 발생, 재시도 {attempt}/{retries}")
                print(e)
                time.sleep(delay * attempt)
                continue

            raise

    raise Exception("Notion API 재시도 실패")


def get_all_pages(data_source_id):
    pages = []
    cursor = None

    while True:
        kwargs = {
            "data_source_id": data_source_id,
            "page_size": 100
        }

        if cursor:
            kwargs["start_cursor"] = cursor

        result = notion_call(notion.data_sources.query, **kwargs)
        pages.extend(result["results"])

        if not result.get("has_more"):
            break

        cursor = result.get("next_cursor")

    return pages


def get_text(prop):
    if prop["type"] == "title":
        return "".join([t["plain_text"] for t in prop["title"]])

    if prop["type"] == "rich_text":
        return "".join([t["plain_text"] for t in prop["rich_text"]])

    return ""


def get_title(page):
    return get_text(page["properties"]["프로젝트 이름"])


def get_team_name(data_source_id):
    ds = notion_call(
        notion.data_sources.retrieve,
        data_source_id=data_source_id
    )

    parent_db_id = ds["parent"]["database_id"]

    db = notion_call(
        notion.databases.retrieve,
        database_id=parent_db_id
    )

    title = "".join([t["plain_text"] for t in db["title"]])

    return (
        title
        .replace(" Project", "")
        .replace(" PROJECT", "")
        .replace(" project", "")
        .replace("프로젝트", "")
        .strip()
    )


def get_people_ids(prop):
    return [person["id"] for person in prop.get("people", [])]


def get_prop_compare_value(prop):
    """
    비교용 값 추출.
    이 함수는 현재 코드에서 복사하는 속성만 비교하기 위한 용도.
    """
    prop_type = prop["type"]

    if prop_type == "title":
        return "".join([t["plain_text"] for t in prop["title"]])

    if prop_type == "rich_text":
        return "".join([t["plain_text"] for t in prop["rich_text"]])

    if prop_type == "select":
        if prop["select"]:
            return prop["select"]["name"]
        return None

    if prop_type == "date":
        return prop["date"]

    if prop_type == "people":
        return get_people_ids(prop)

    return None


def get_new_prop_compare_value(prop):
    """
    새로 업데이트하려는 new_props 기준 비교값 추출.
    """
    if "title" in prop:
        return "".join([t["text"]["content"] for t in prop["title"]])

    if "rich_text" in prop:
        return "".join([t["text"]["content"] for t in prop["rich_text"]])

    if "status" in prop:
        return prop["status"]["name"]

    if "select" in prop:
        return prop["select"]["name"]

    if "date" in prop:
        return prop["date"]

    if "people" in prop:
        return [person["id"] for person in prop["people"]]

    return None


def is_same_properties(target_page, new_props):
    """
    기존 통합 DB 페이지와 새로 반영할 속성이 같은지 비교.
    new_props에 들어있는 속성만 비교한다.
    """
    target_props = target_page["properties"]

    for prop_name, new_prop in new_props.items():
        if prop_name not in target_props:
            return False

        old_value = get_prop_compare_value(target_props[prop_name])
        new_value = get_new_prop_compare_value(new_prop)

        if old_value != new_value:
            return False

    return True


def make_target_page_map(target_pages):
    """
    통합 DB 전체 페이지를 원본 page ID 기준으로 딕셔너리화.
    기존처럼 원본 page ID로 매번 query하지 않기 때문에 훨씬 빠르다.
    """
    result = {}

    for page in target_pages:
        props = page["properties"]

        if "원본 page ID" not in props:
            continue

        source_page_id = get_text(props["원본 page ID"])

        if source_page_id:
            result[source_page_id] = page

    return result


total_added = 0
total_updated = 0
total_skipped = 0
total_deleted = 0
total_source_projects = 0

all_source_page_ids = set()

team_stats = {}

# ==============================
# 통합 DB를 먼저 한 번만 읽기
# ==============================
target_pages_before_sync = get_all_pages(TARGET_DB_ID)
target_page_map = make_target_page_map(target_pages_before_sync)


# ==============================
# 원본 DB → 통합 DB 동기화
# ==============================
for source in SOURCE_DBS:
    source_id = source["id"]
    team_name = get_team_name(source_id)

    all_pages = get_all_pages(source_id)

    for p in all_pages:
        all_source_page_ids.add(p["id"])

    total_source_projects += len(all_pages)

    team_stats[team_name] = {
        "source_count": len(all_pages),
        "added": 0,
        "updated": 0,
        "skipped": 0,
        "deleted": 0
    }

    if TEST_LIMIT_PER_DB is None:
        pages = all_pages
    else:
        pages = all_pages[:TEST_LIMIT_PER_DB]

    for page in pages:
        source_page_id = page["id"]

        props = page["properties"]
        project_name = get_title(page)

        new_props = {
            "프로젝트 이름": {
                "title": [
                    {
                        "text": {
                            "content": project_name
                        }
                    }
                ]
            },
            "원본 page ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": source_page_id
                        }
                    }
                ]
            },
            "팀": {
                "rich_text": [
                    {
                        "text": {
                            "content": team_name
                        }
                    }
                ]
            }
        }

        if "시작일" in props and props["시작일"]["date"]:
            new_props["시작일"] = {
                "date": props["시작일"]["date"]
            }

        if "종료일" in props and props["종료일"]["date"]:
            new_props["종료일"] = {
                "date": props["종료일"]["date"]
            }

        if "중요도" in props and props["중요도"]["select"]:
            new_props["중요도"] = {
                "select": {
                    "name": props["중요도"]["select"]["name"]
                }
            }

        if "담당자" in props and props["담당자"]["people"]:
            new_props["담당자"] = {
                "people": [
                    {"id": person["id"]}
                    for person in props["담당자"]["people"]
                ]
            }

        if "요청자" in props and props["요청자"]["people"]:
            new_props["요청자"] = {
                "people": [
                    {"id": person["id"]}
                    for person in props["요청자"]["people"]
                ]
            }

        try:
            target_page = target_page_map.get(source_page_id)

            if target_page:
                target_page_id = target_page["id"]

                if is_same_properties(target_page, new_props):
                    total_skipped += 1
                    team_stats[team_name]["skipped"] += 1

                else:
                    notion_call(
                        notion.pages.update,
                        page_id=target_page_id,
                        properties=new_props
                    )

                    total_updated += 1
                    team_stats[team_name]["updated"] += 1

            else:
                created_page = notion_call(
                    notion.pages.create,
                    parent={
                        "data_source_id": TARGET_DB_ID
                    },
                    properties=new_props
                )

                target_page_map[source_page_id] = created_page

                total_added += 1
                team_stats[team_name]["added"] += 1

        except Exception as e:
            print("오류 발생:", team_name, "/", project_name)
            print(e)
            print("계속 진행")
            print("-" * 30)
            continue


# ==============================
# 삭제 대상 확인 및 보관 처리
# ==============================
delete_candidates = []

for page in target_pages_before_sync:
    props = page["properties"]

    if "원본 page ID" not in props:
        continue

    source_page_id = get_text(props["원본 page ID"])
    project_name = get_text(props["프로젝트 이름"])

    if "팀" in props:
        team_name = get_text(props["팀"])
    else:
        team_name = "팀 정보 없음"

    if source_page_id and source_page_id not in all_source_page_ids:
        delete_candidates.append({
            "project_name": project_name,
            "target_page_id": page["id"],
            "source_page_id": source_page_id,
            "team_name": team_name
        })


for item in delete_candidates:
    try:
        notion_call(
            notion.pages.update,
            page_id=item["target_page_id"],
            archived=True
        )

        total_deleted += 1

        team_name = item["team_name"]

        if team_name not in team_stats:
            team_stats[team_name] = {
                "source_count": 0,
                "added": 0,
                "updated": 0,
                "skipped": 0,
                "deleted": 0
            }

        team_stats[team_name]["deleted"] += 1

    except Exception as e:
        print("삭제 오류 발생:", item["team_name"], "/", item["project_name"])
        print(e)
        print("계속 진행")
        print("-" * 30)
        continue


# ==============================
# 최종 요약 출력 - GitHub Actions 로그 메일용
# NO + 숫자열 정렬 + 팀명 맨 뒤
# ==============================

# ==============================
# 최종 요약 출력 - GitHub Actions 로그 메일용
# NO 2자리 + 수량 3자리 + 열 간격 확대
# ==============================

# ==============================
# 최종 요약 출력 - GitHub Actions 로그 메일용
# NO 2자리 + 수량 3자리 + 열 간격 확대
# ==============================

# ==============================
# 최종 요약 출력 - GitHub Actions 로그 메일용
# NO 2자리 + 수량 3자리 + 열 간격 확대
# ==============================

NO_W = 2
COUNT_W = 3

SEP = "  |  "
TOTAL_FIRST_SEP = "  |  "   # 계 행에서 개수 값부터 왼쪽으로 2칸 이동

TEAM_HEADER_GAP = " " * 3
TEAM_VALUE_GAP = " " * 4

NO_VALUE_GAP = " " * 1
COUNT_VALUE_GAP = " " * 2
ADD_VALUE_GAP = " " * 2
UPDATE_VALUE_GAP = " " * 2
SKIP_VALUE_GAP = " " * 3
DELETE_VALUE_GAP = " " * 2


def fmt_count(value):
    return f"{value:03d}"


print("")
print("[프로젝트 씽크] 성공")
print("=" * 50)

print(
    f"{'NO':>{NO_W}}"
    f"{SEP}"
    f"{'개수':>{COUNT_W}}"
    f"{SEP}"
    f"{'추가':>{COUNT_W}}"
    f"{SEP}"
    f"{'수정':>{COUNT_W}}"
    f"{SEP}"
    f"{'건너뜀':>{COUNT_W}}"
    f"{SEP}"
    f"{'삭제':>{COUNT_W}}"
    f"{SEP}"
    f"{TEAM_HEADER_GAP}팀명"
)

print("-" * 85)

for idx, (team_name, stat) in enumerate(team_stats.items(), start=1):
    print(
        f"{NO_VALUE_GAP}{idx:02d}"
        f"{SEP}"
        f"{COUNT_VALUE_GAP}{fmt_count(stat['source_count'])}"
        f"{SEP}"
        f"{ADD_VALUE_GAP}{fmt_count(stat['added'])}"
        f"{SEP}"
        f"{UPDATE_VALUE_GAP}{fmt_count(stat['updated'])}"
        f"{SEP}"
        f"{SKIP_VALUE_GAP}{fmt_count(stat['skipped'])}"
        f"{SEP}"
        f"{DELETE_VALUE_GAP}{fmt_count(stat['deleted'])}"
        f"{SEP}"
        f"{TEAM_VALUE_GAP}{team_name}"
    )

print("-" * 85)

print(
    f"{' 계'}"
    f"{TOTAL_FIRST_SEP}"
    f"{COUNT_VALUE_GAP}{fmt_count(total_source_projects)}"
    f"{SEP}"
    f"{ADD_VALUE_GAP}{fmt_count(total_added)}"
    f"{SEP}"
    f"{UPDATE_VALUE_GAP}{fmt_count(total_updated)}"
    f"{SEP}"
    f"{SKIP_VALUE_GAP}{fmt_count(total_skipped)}"
    f"{SEP}"
    f"{DELETE_VALUE_GAP}{fmt_count(total_deleted)}"
    f"{SEP}"
    f"{TEAM_VALUE_GAP}"
)

print("=" * 50)

