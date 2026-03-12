import requests
import os
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

tasks = []
seen_ids = set()

for page in range(1, 10):

    url = f"https://api.weeek.net/public/v1/tm/tasks?workspaceId={WORKSPACE_ID}&page={page}&limit=100"

    response = requests.get(url, headers=headers).json()

    page_tasks = response.get("tasks", [])

    if not page_tasks:
        break

    for task in page_tasks:

        if task["id"] not in seen_ids:
            tasks.append(task)
            seen_ids.add(task["id"])

print("TOTAL TASKS:", len(tasks))

projects_url = f"https://api.weeek.net/public/v1/tm/projects?workspaceId={WORKSPACE_ID}"

projects = requests.get(projects_url, headers=headers).json()["projects"]

project_map = {p["id"]: p["title"] for p in projects}

today = datetime.today().date()

today_iso = today.strftime("%Y-%m-%d")
today_ru = today.strftime("%d.%m.%Y")

today_tasks = {}

for task in tasks:

    if task.get("parentId") is not None:
        continue

    due = str(task.get("dueDate", ""))[:10]
    date = str(task.get("date", ""))

    if due != today_iso and date != today_ru:
        continue

    project_id = task.get("projectId")
    project_name = project_map.get(project_id, "Без проекта")

    today_tasks.setdefault(project_name, []).append(task)

message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

keyboard = []

if not today_tasks:
    message += "Сегодня задач нет"

else:

    for project, tasks_list in today_tasks.items():

        message += f"📂 {project}\n"

        for task in tasks_list:

            message += f"• {task['title']}\n"

            keyboard.append([
                {
                    "text": "Открыть задачу",
                    "url": f"https://app.weeek.net/ws/{WORKSPACE_ID}/task/{task['id']}"
                }
            ])

        message += "\n"

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "reply_markup": {
        "inline_keyboard": keyboard
    }
}

response = requests.post(telegram_url, json=payload)

print(response.text)
