import os
import requests
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

BASE_URL = "https://api.weeek.net/public/v1/tm/tasks"

today = datetime.now().strftime("%d.%m.%Y")

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

params = {
    "workspaceId": WORKSPACE_ID,
    "startDate": today,
    "endDate": today,
    "completed": 0,
    "limit": 100
}

print("REQUEST PARAMS:", params)

response = requests.get(BASE_URL, headers=headers, params=params)

data = response.json()

tasks = data.get("tasks", [])

print("TODAY TASKS FROM API:", len(tasks))

projects = {}

for task in tasks:

    project = task.get("project", {}).get("name", "Без проекта")

    if project not in projects:
        projects[project] = []

    projects[project].append(task)

message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

if not tasks:
    message += "Сегодня задач нет 🎉"

for project, project_tasks in projects.items():

    message += f"📂 {project}\n"

    for task in project_tasks:
        message += f"• {task['title']}\n"

    message += "\n"

buttons = []

for task in tasks:

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
