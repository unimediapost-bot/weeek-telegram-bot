import os
import requests
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

BASE_URL = "https://api.weeek.net/public/v1/tm/tasks"

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

today = datetime.now().strftime("%Y-%m-%d")

limit = 100
offset = 0
all_tasks = []

print("START LOADING TASKS")

while True:

    params = {
        "workspaceId": WORKSPACE_ID,
        "limit": limit,
        "offset": offset
    }

    response = requests.get(BASE_URL, headers=headers, params=params)
    data = response.json()

    tasks = data.get("tasks", [])

    print(f"PAGE OFFSET {offset} | TASKS: {len(tasks)}")

    all_tasks.extend(tasks)

    if not data.get("hasMore"):
        break

    offset += limit


print("TOTAL TASKS LOADED:", len(all_tasks))

today_tasks = []

for task in all_tasks:

    start = task.get("dateStart")
    end = task.get("dateEnd")

    if start == today or end == today:
        today_tasks.append(task)

print("TODAY TASKS FOUND:", len(today_tasks))

# группируем по проектам
projects = {}

for task in today_tasks:

    project_name = f"Проект {task.get('projectId')}"

    if project_name not in projects:
        projects[project_name] = []

    projects[project_name].append(task)


message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

if not today_tasks:
    message += "Сегодня задач нет 🎉"

for project, tasks in projects.items():

    message += f"📂 {project}\n"

    for task in tasks:
        message += f"• {task['title']}\n"

    message += "\n"


buttons = []

for task in today_tasks:

    buttons.append([
        {
            "text": "Открыть задачу",
            "url": f"https://app.weeek.net/ws/{WORKSPACE_ID}/task/{task['id']}"
        }
    ])


telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "reply_markup": {
        "inline_keyboard": buttons
    }
}

response = requests.post(telegram_url, json=payload)

print("TELEGRAM RESPONSE:")
print(response.text)
