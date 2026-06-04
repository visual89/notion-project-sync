import os
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

        result = notion.data_sources.query(**kwargs)
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
    result = notion.data_sources.query(
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


total_added = 0
total_updated = 0
all_source_page_ids = set()

for source in SOURCE_DBS:
    source_id = source["id"]
    team_name = get_team_name(source_id)

    print("=" * 50)
    print("처리중:", team_name)

    all_pages = get_all_pages(source_id)

    for p in all_pages:
        all_source_page_ids.add(p["id"])

    print("원본 전체 프로젝트 수:", len(all_pages))

    if TEST_LIMIT_PER_DB is None:
        pages = all_pages
    else:
        pages = all_pages[:TEST_LIMIT_PER_DB]

    print("이번 실행 처리 수:", len(pages))

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
            # 중요도 복사
        if "중요도" in props and props["중요도"]["select"]:
            new_props["중요도"] = {
                "select": {
                    "name": props["중요도"]["select"]["name"]
                }
            }

        # 담당자 복사
        if "담당자" in props and props["담당자"]["people"]:
            new_props["담당자"] = {
                "people": [
                    {"id": person["id"]}
                    for person in props["담당자"]["people"]
                ]
            }

        # 요청자 복사
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
                print("수정:", project_name)
            else:
                notion.pages.create(
                    parent={
                        "data_source_id": TARGET_DB_ID
                    },
                    properties=new_props
                )
                total_added += 1
                print("추가:", project_name)

        except Exception as e:
            print("오류 발생:", project_name)
            print(e)
            print("계속 진행")
            print("-" * 30)
            continue


print("=" * 50)
print("삭제 예정 확인")

target_pages = get_all_pages(TARGET_DB_ID)

delete_candidates = []

for page in target_pages:
    props = page["properties"]

    if "원본 page ID" not in props:
        continue

    source_page_id = get_text(props["원본 page ID"])
    project_name = get_text(props["프로젝트 이름"])

    if source_page_id and source_page_id not in all_source_page_ids:
        delete_candidates.append({
            "project_name": project_name,
            "target_page_id": page["id"],
            "source_page_id": source_page_id
        })

print("삭제 대상 개수:", len(delete_candidates))

for item in delete_candidates:

    print("삭제:", item["project_name"])

    notion.pages.update(
        page_id=item["target_page_id"],
        archived=True
    )

    print("삭제 완료")
    print("-" * 30)

print("=" * 50)
print("총 추가:", total_added)
print("총 수정:", total_updated)
print("총 삭제:", len(delete_candidates))
print("완료")
