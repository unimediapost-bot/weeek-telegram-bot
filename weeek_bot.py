import os
import requests
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

today = datetime.now().strftime("%Y-%m-%d")

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

all_tasks = []

limit = 100
offset = 0

print("START LOADING TASKS")

while True:

    url = f"https://api.weeek.net/public/v1/tm/tasks?workspaceId={WORKSPACE_ID}&limit={limit}&offset={offset}"

    print("REQUEST:", url)

    response = requests.get(url, headers=headers)
    data = response.json()

    tasks = data.get("tasks", [])

    print("TASKS RECEIVED:", len(tasks))

    if not tasks:
        break

    all_tasks.extend(tasks)

    if len(tasks) < limit:
        break

    offset += limit


print("TOTAL TASKS:", len(all_tasks))

today_tasks = []

for task in all_tasks:

    date = task.get("date")
    due = task.get("dueDate")

    if date == today or due == today:
        today_tasks.append(task)

print("TODAY TASKS:", len(today_tasks))

projects = {}

for task in today_tasks:

    project = task.get("project", {}).get("name", "Без проекта")

    if project not in projects:
        projects[project] = []

    projects[project].append(task)

message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

if not projects:
    message += "Сегодня задач нет"

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
