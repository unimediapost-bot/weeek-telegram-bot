import requests
import os
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

tasks_url = "https://api.weeek.net/public/v1/tm/tasks?limit=100"
projects_url = "https://api.weeek.net/public/v1/tm/projects"

tasks = requests.get(tasks_url, headers=headers).json()["tasks"]
projects = requests.get(projects_url, headers=headers).json()["projects"]

project_map = {p["id"]: p["title"] for p in projects}

today = datetime.today().date()

today_tasks = {}

for task in tasks:

    # берём только основные задачи
    if task.get("parentId") is not None:
        continue

    task_date = None

    if task.get("dueDate"):
        task_date = datetime.strptime(task["dueDate"], "%Y-%m-%d").date()

    elif task.get("date"):
        task_date = datetime.strptime(task["date"], "%d.%m.%Y").date()

    if task_date != today:
        continue

    project_id = task.get("projectId")
    project_name = project_map.get(project_id, "Без проекта")

    today_tasks.setdefault(project_name, []).append(task)


message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

keyboard = []

if not today_tasks:

    message += "Нет задач"

else:

    for project, tasks_list in today_tasks.items():

        message += f"📂 {project}\n"

        for task in tasks_list:

            message += f"• {task['title']}\n"

            keyboard.append([
                {
                    "text": f"Открыть: {task['title']}",
                    "url": f"https://app.weeek.net/ws/1/task/{task['id']}"
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
