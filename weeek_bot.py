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

today = datetime.now().strftime("%d.%m.%Y")

# -------------------------
# загрузка проектов
# -------------------------

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

# -------------------------
# загрузка задач
# -------------------------

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

# -------------------------
# фильтрация задач
# -------------------------

today_tasks = []

for task in all_tasks:

    # игнорируем подзадачи
    if task.get("parentId"):
        continue

    workloads = task.get("workloads", [])

    for w in workloads:
        if w.get("date") == today:
            today_tasks.append(task)
            break

print("TODAY TASKS FOUND:", len(today_tasks))

# -------------------------
# группировка по проектам
# -------------------------

grouped = {}

for task in today_tasks:

    project_id = task.get("projectId")

    project_name = projects.get(project_id, "Без проекта")

    if project_name not in grouped:
        grouped[project_name] = []

    grouped[project_name].append(task)

# -------------------------
# сообщение
# -------------------------

message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

if not grouped:
    message += "Сегодня задач нет 🎉"

for project, tasks in grouped.items():

    message += f"📂 {project}\n"

    for task in tasks:
        message += f"- {task['title']}\n"

    message += "\n"

# -------------------------
# отправка в Telegram
# -------------------------

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(telegram_url, json=payload)

print("TELEGRAM RESPONSE:")
print(response.text)

# ОТЛАДКА - удалить после проверки
print("\n=== ПЕРВЫЕ 5 ЗАДАЧ (сырые данные) ===")
for task in all_tasks[:5]:
    print({
        "title": task.get("title"),
        "date": task.get("date"),
        "dateStart": task.get("dateStart"),
        "dueDate": task.get("dueDate"),
        "isCompleted": task.get("isCompleted"),
        "parentId": task.get("parentId"),
    })
print(f"\nСегодня (today): '{today}'")
print("=====================================\n")
