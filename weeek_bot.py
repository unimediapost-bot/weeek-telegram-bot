import os
import requests
import json
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

BASE_URL = "https://api.weeek.net/public/v1/tm/tasks"
PROJECTS_URL = "https://api.weeek.net/public/v1/tm/projects"

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

today_iso = datetime.now().strftime("%Y-%m-%d")
today_dot = datetime.now().strftime("%d.%m.%Y")

# -----------------------------
# Проверка переменных окружения
# -----------------------------
missing = [v for v, val in {
    "WEEEK_TOKEN": WEEEK_TOKEN,
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "CHAT_ID": CHAT_ID,
    "WORKSPACE_ID": WORKSPACE_ID
}.items() if not val]

if missing:
    raise EnvironmentError(f"Не заданы переменные окружения: {', '.join(missing)}")

# -----------------------------
# получаем список проектов
# -----------------------------
projects = {}
r = requests.get(PROJECTS_URL, headers=headers, params={"workspaceId": WORKSPACE_ID})
r.raise_for_status()
for p in r.json().get("projects", []):
    projects[p["id"]] = p["title"]

print("PROJECTS LOADED:", len(projects))

# -----------------------------
# тестируем разные форматы day
# -----------------------------
for fmt in [today_iso, today_dot, today_iso.replace("-", "")]:
    r = requests.get(BASE_URL, headers=headers, params={
        "workspaceId": WORKSPACE_ID,
        "day": fmt,
        "offset": 0
    })
    print(f"day={fmt} → status={r.status_code} | response={r.text[:300]}")
