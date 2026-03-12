import os
import requests
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

today = datetime.now().strftime("%Y-%m-%d")

# -----------------------------
# получаем список проектов
# -----------------------------

projects = {}

r = requests.get(
    PROJECTS_URL,
    headers=headers,
    params={"workspaceId": WORKSPACE_ID}
)

data = r.json()

for p in data.get("projects", []):
    projects[p["id"]] = p["title"]

print("PROJECTS LOADED:", len(projects))


# -----------------------------
# загружаем задачи
# -----------------------------

offset = 0
all_tasks = []

print("START LOADING TASKS")

while True:

    params = {
        "workspaceId": WORKSPACE_ID,
        "offset": offset
    }

    r = requests.get(BASE_URL, headers=headers, params=params)
    data = r.json()

    tasks = data.get("tasks", [])

    print(f"OFFSET {offset} | TASKS: {len(tasks)}")

    if not tasks:
        break

    all_tasks.extend(tasks)

    if not data.get("hasMore"):
        break

    offset += len(tasks)

print("TOTAL TASKS LOADED:", len(all_tasks))


# -----------------------------
# фильтрация задач
# -----------------------------

today_tasks = []

for task in all_tasks:

    # игнорируем подзадачи
    if task.get("parentId"):
        continue

    task_date = (
        task.get("date")
        or task.get("dateStart")
        or task.get("dueDate")
    )

    if task_date == today and not task.get("isCompleted"):
        today_tasks.append(task)

print("TODAY TASKS FOUND:", len(today_tasks))


# -----------------------------
# группируем по проектам
# -----------------------------

grouped = {}

for task in today_tasks:

    project_id = task.get("projectId")

    project_name = projects.get(project_id, "Без проекта")

    if project_name not in grouped:
        grouped[project_name] = []

    grouped[project_name].append(task)


# -----------------------------
# формируем сообщение
# -----------------------------

message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

if not grouped:
    message += "Сегодня задач нет 🎉"

for project, tasks in grouped.items():

    message += f"📂 {project}\n"

    for task in tasks:
        message += f"- {task['title']}\n"

    message += "\n"


# -----------------------------
# отправляем в Telegram
# -----------------------------

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(telegram_url, json=payload)

print("TELEGRAM RESPONSE:")
print(response.text)
