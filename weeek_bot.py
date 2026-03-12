import os
import requests
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
BOT_MODE = os.getenv("BOT_MODE", "morning")  # morning или midday

BASE_URL = "https://api.weeek.net/public/v1/tm/tasks"
PROJECTS_URL = "https://api.weeek.net/public/v1/tm/projects"

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

today = datetime.now().strftime("%d.%m.%Y")
today_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

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

print(f"BOT_MODE: {BOT_MODE}")

# -----------------------------
# получаем список проектов
# -----------------------------
projects = {}
r = requests.get(PROJECTS_URL, headers=headers, params={"workspaceId": WORKSPACE_ID})
r.raise_for_status()
for p in r.json().get("projects", []):
    projects[p["id"]] = p["title"]

print("PROJECTS LOADED:", len(projects))

# -----------------------------
# вспомогательные функции
# -----------------------------
def load_tasks(params):
    offset = 0
    all_tasks = []
    while True:
        params["offset"] = offset
        r = requests.get(BASE_URL, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        tasks = data.get("tasks", [])
        if not tasks:
            break
        all_tasks.extend(tasks)
        if not data.get("hasMore"):
            break
        offset += len(tasks)
    return all_tasks

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:10], "%d.%m.%Y")
    except:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except:
            return None

def group_by_project(tasks):
    grouped = {}
    for task in tasks:
        project_id = task.get("projectId")
        project_name = projects.get(project_id, "Без проекта")
        if project_name not in grouped:
            grouped[project_name] = []
        grouped[project_name].append(task)
    return grouped

# -----------------------------
# загружаем задачи на сегодня
# -----------------------------
print(f"LOADING TASKS FOR DAY: {today}")
today_tasks_raw = load_tasks({"workspaceId": WORKSPACE_ID, "day": today})

print("LOADING OVERDUE TASKS")
overdue_tasks_raw = load_tasks({"workspaceId": WORKSPACE_ID, "overdue": "true"})

# -----------------------------
# фильтруем родительские задачи
# -----------------------------
today_all = [
    t for t in today_tasks_raw
    if t.get("parentId") is None
]

today_done = [t for t in today_all if t.get("isCompleted")]
today_pending = [t for t in today_all if not t.get("isCompleted")]

overdue_tasks = [
    t for t in overdue_tasks_raw
    if t.get("parentId") is None
    and not t.get("isCompleted")
    and parse_date(t.get("dueDate") or t.get("date")) is not None
    and parse_date(t.get("dueDate") or t.get("date")) < today_dt
]

print(f"TODAY PENDING: {len(today_pending)} | DONE: {len(today_done)} | OVERDUE: {len(overdue_tasks)}")

# -----------------------------
# формируем сообщение
# -----------------------------
if BOT_MODE == "morning":
    message = "Доброе утро!\n\n"
    message += f"📅 Задачи на сегодня {today}\n\n"

    grouped = group_by_project(today_pending)
    if not grouped:
        message += "Сегодня задач нет 🎉\n"
    else:
        for project, tasks in grouped.items():
            message += f"📂 {project}\n"
            for task in tasks:
                message += f"- {task.get('title', '(без названия)')}\n"
            message += "\n"

    if overdue_tasks:
        message += "⚠️ Просроченные задачи\n\n"
        for project, tasks in group_by_project(overdue_tasks).items():
            message += f"📂 {project}\n"
            for task in tasks:
                due = task.get("dueDate") or task.get("date") or ""
                message += f"- {task.get('title', '(без названия)')} ({due})\n"
            message += "\n"

else:  # midday
    message = "☀️ Промежуточный итог\n\n"

    if today_done:
        message += "✅ Выполнено\n\n"
        for project, tasks in group_by_project(today_done).items():
            message += f"📂 {project}\n"
            for task in tasks:
                message += f"- {task.get('title', '(без названия)')}\n"
            message += "\n"

    if today_pending:
        message += "🔲 Ещё не выполнено\n\n"
        for project, tasks in group_by_project(today_pending).items():
            message += f"📂 {project}\n"
            for task in tasks:
                message += f"- {task.get('title', '(без названия)')}\n"
            message += "\n"

    if not today_done and not today_pending:
        message += "Задач на сегодня нет 🎉\n"

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
