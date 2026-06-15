import os
import time
import html
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
    ds = notion.data_sources.retrieve(data_source_id=data_source_id)
    parent_db_id = ds["parent"]["database_id"]
    db = notion.databases.retrieve(database_id=parent_db_id)

    title = "".join([t["plain_text"] for t in db["title"]])

    return (
        title
        .replace(" Project", "")
        .replace(" PROJECT", "")
        .replace(" project", "")
        .replace("프로젝트", "")
        .strip()
    )


def find_target_page(source_page_id):
    result = notion_call(
        notion.data_sources.query,
        data_source_id=TARGET_DB_ID,
        filter={
            "property": "원본 page ID",
            "rich_text": {
                "equals": source_page_id
            }
        },
        page_size=1
    )

    if result["results"]:
        return result["results"][0]["id"]

    return None


def build_html_summary(
    team_stats,
    total_source_projects,
    total_added,
    total_updated,
    total_deleted
):
    rows = ""

    for team_name, stat in team_stats.items():
        rows += f"""
            <tr>
                <td>{html.escape(str(team_name))}</td>
                <td class="num">{stat["source_count"]}</td>
                <td class="num">{stat["added"]}</td>
                <td class="num">{stat["updated"]}</td>
                <td class="num">{stat["deleted"]}</td>
            </tr>
        """

    html_result = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, 'Malgun Gothic', sans-serif;
            font-size: 14px;
            color: #222;
        }}

        h2 {{
            margin-bottom: 12px;
        }}

        table {{
            border-collapse: collapse;
            width: 760px;
            max-width: 100%;
        }}

        th, td {{
            border: 1px solid #d9d9d9;
            padding: 7px 10px;
            line-height: 1.4;
        }}

        th {{
            background-color: #f3f5f7;
            font-weight: bold;
            text-align: center;
        }}

        td {{
            text-align: left;
        }}

        .num {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}

        .total-row td {{
            background-color: #fafafa;
            font-weight: bold;
        }}

        .done {{
            margin-top: 14px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h2>프로젝트 동기화 결과</h2>

    <table>
        <thead>
            <tr>
                <th>팀명</th>
                <th>원본 프로젝트 수</th>
                <th>추가</th>
                <th>수정</th>
                <th>삭제</th>
            </tr>
        </thead>
        <tbody>
            {rows}
            <tr class="total-row">
                <td>합계</td>
                <td class="num">{total_source_projects}</td>
                <td class="num">{total_added}</td>
                <td class="num">{total_updated}</td>
                <td class="num">{total_deleted}</td>
            </tr>
        </tbody>
    </table>

    <div class="done">완료</div>
</body>
</html>
"""

    return html_result


total_added = 0
total_updated = 0
total_deleted = 0
total_source_projects = 0

all_source_page_ids = set()

team_stats = {}

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
        "deleted": 0
    }

    if TEST_LIMIT_PER_DB is None:
        pages = all_pages
    else:
        pages = all_pages[:TEST_LIMIT_PER_DB]

    for page in pages:
        source_page_id = page["id"]
        target_page_id = find_target_page(source_page_id)

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

        if "상태" in props and props["상태"]["status"]:
            new_props["상태"] = {
                "status": {
                    "name": props["상태"]["status"]["name"]
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
            if target_page_id:
                notion.pages.update(
                    page_id=target_page_id,
                    properties=new_props
                )
                total_updated += 1
                team_stats[team_name]["updated"] += 1

            else:
                notion.pages.create(
                    parent={
                        "data_source_id": TARGET_DB_ID
                    },
                    properties=new_props
                )
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
target_pages = get_all_pages(TARGET_DB_ID)

delete_candidates = []

for page in target_pages:
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
        notion.pages.update(
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
# 최종 요약 출력 - HTML 표
# ==============================
html_result = build_html_summary(
    team_stats=team_stats,
    total_source_projects=total_source_projects,
    total_added=total_added,
    total_updated=total_updated,
    total_deleted=total_deleted
)

print(html_result)
