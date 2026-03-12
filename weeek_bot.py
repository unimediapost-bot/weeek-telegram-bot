import os
import requests
import json

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

headers = {"Authorization": f"Bearer {WEEEK_TOKEN}"}
today = "12.03.2026"

r = requests.get(
    "https://api.weeek.net/public/v1/tm/tasks",
    headers=headers,
    params={"workspaceId": WORKSPACE_ID, "day": today, "offset": 0}
)

tasks = r.json().get("tasks", [])
for t in tasks:
    if t.get("assignees"):
        print(json.dumps({
            "title": t.get("title"),
            "assignees": t.get("assignees"),
            "userId": t.get("userId"),
        }, indent=2, ensure_ascii=False))
