import os
import requests
from datetime import datetime, timedelta

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

headers = {"Authorization": f"Bearer {WEEEK_TOKEN}"}

yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

# тест 1 — параметр dayTo (все задачи до вчера)
r = requests.get(
    "https://api.weeek.net/public/v1/tm/tasks",
    headers=headers,
    params={"workspaceId": WORKSPACE_ID, "dayTo": yesterday, "offset": 0}
)
print(f"dayTo={yesterday} → status={r.status_code} | {r.text[:300]}")

# тест 2 — параметр overdue
r2 = requests.get(
    "https://api.weeek.net/public/v1/tm/tasks",
    headers=headers,
    params={"workspaceId": WORKSPACE_ID, "overdue": True, "offset": 0}
)
print(f"overdue=true → status={r2.status_code} | {r2.text[:300]}")
