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
r = requests.get(
    PROJECTS_URL,
    headers=headers,
    params={"workspaceId": WORKSPACE_ID}
)
r.raise_for_status()
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
        "offset": offset,
        "isParent": True  # только родительские задачи
    }
    r = requests.get(BASE_URL, headers=headers, params=params)
    r.raise_for_status()
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
# отладка — удалить после проверки
# -----------------------------
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

# -----------------------------
# фильтрация задач
# -----------------------------
today_tasks = []
for task in all_tasks:
    task_date = (
        task.get("date")
        or task.get("dateStart")
        or task.get("dueDate")
    )

    if task_date and task_date[:10] == today and not task.get("isCompleted"):
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
else:
    for project, tasks in grouped.items():
        message += f"📂 {project}\n"
        for task in tasks:
            title = task.get("title", "(без названия)")
            message += f"- {title}\n"
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
response.raise_for_status()
print("TELEGRAM RESPONSE:")
print(response.text)

# -----------------------------
# отладка — удалить после проверки
# -----------------------------
print("\n=== ПОЛНАЯ СТРУКТУРА ПЕРВОЙ ЗАДАЧИ ===")
if all_tasks:
    import json
    print(json.dumps(all_tasks[0], indent=2, ensure_ascii=False))
print("=====================================\n")
