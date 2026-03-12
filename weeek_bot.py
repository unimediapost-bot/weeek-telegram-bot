import requests
import os
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

tasks_url = "https://api.weeek.net/public/v1/tm/tasks"
projects_url = "https://api.weeek.net/public/v1/tm/projects"

tasks = requests.get(tasks_url, headers=headers).json()["tasks"]
projects = requests.get(projects_url, headers=headers).json()["projects"]

# карта проектов
project_map = {p["id"]: p["title"] for p in projects}

# группировка задач
projects_tasks = {}

for task in tasks:

    project_id = task.get("projectId")
    title = task.get("title")
    task_id = task.get("id")

    project_name = project_map.get(project_id, "Без проекта")

    projects_tasks.setdefault(project_name, []).append({
        "title": title,
        "id": task_id
    })


message = "Доброе утро!\n\n"

keyboard = []

for project, items in projects_tasks.items():

    message += f"📂 {project}\n"

    for t in items:

        message += f"• {t['title']}\n"

        keyboard.append([
            {
                "text": f"Открыть: {t['title']}",
                "url": f"https://app.weeek.net/ws/1/task/{t['id']}"
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
