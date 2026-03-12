import requests
import os
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

# ---------- загрузка всех задач ----------

tasks = []
page = 1

while True:

    url = f"https://api.weeek.net/public/v1/tm/tasks?page={page}&limit=100"

    response = requests.get(url, headers=headers).json()

    page_tasks = response.get("tasks", [])

    if not page_tasks:
        break

    tasks.extend(page_tasks)

    page += 1

print("TOTAL TASKS:", len(tasks))

# ---------- загрузка проектов ----------

projects_url = "https://api.weeek.net/public/v1/tm/projects"

projects = requests.get(projects_url, headers=headers).json()["projects"]

project_map = {p["id"]: p["title"] for p in projects}

# ---------- фильтрация задач ----------

today = datetime.today().date()

today_tasks = {}

for task in tasks:

    # пропускаем подзадачи
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

# ---------- формирование сообщения ----------

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

# ---------- отправка в Telegram ----------

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "reply_markup": {
        "inline_keyboard": keyboard
    }
}

response = requests.post(telegram_url, json=payload)

print("Telegram response:")
print(response.text)
