import os
import requests
from datetime import datetime

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

BASE_URL = "https://api.weeek.net/public/v1/tm/tasks"
PROJECTS_URL = "https://api.weeek.net/public/v1/tm/projects"
MEMBERS_URL = "https://api.weeek.net/public/v1/workspace/members"

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
# получаем список участников
# -----------------------------
members = {}
r = requests.get(MEMBERS_URL, headers=headers, params={"workspaceId": WORKSPACE_ID})
if r.status_code == 200:
    for m in r.json().get("members", []):
        full_name = f"{m.get('firstName', '')} {m.get('lastName', '')}".strip()
        members[str(m["id"])] = full_name
print("MEMBERS LOADED:", len(members))

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

def get_assignee(task):
    assignees = task.get("assignees", [])
    if not assignees:
        return None
    names = [members.get(str(a), str(a)) for a in assignees]
    return ", ".join(n for n in names if n)

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
print(f"TOTAL TODAY TASKS: {len(today_tasks_raw)}")

print("LOADING OVERDUE TASKS")
overdue_tasks_raw = load_tasks({"workspaceId": WORKSPACE_ID, "overdue": "true"})
print(f"TOTAL OVERDUE TASKS RAW: {len(overdue_tasks_raw)}")

# -----------------------------
# фильтруем — только родительские, не завершённые
# -----------------------------
today_tasks = [
    t for t in today_tasks_raw
    if t.get("parentId") is None and not t.get("isCompleted")
]

overdue_tasks = [
    t for t in overdue_tasks_raw
    if t.get("parentId") is None
    and not t.get("isCompleted")
    and parse_date(t.get("dueDate") or t.get("date")) is not None
    and parse_date(t.get("dueDate") or t.get("date")) < today_dt
]

print(f"TODAY PARENT TASKS: {len(today_tasks)}")
print(f"OVERDUE PARENT TASKS: {len(overdue_tasks)}")

# -----------------------------
# группируем по проектам
# -----------------------------
today_grouped = group_by_project(today_tasks)
overdue_grouped = group_by_project(overdue_tasks)

# -----------------------------
# формируем сообщение
# -----------------------------
message = "Доброе утро!\n\n"

# задачи на сегодня
message += f"📅 Задачи на сегодня {today}\n\n"
if not today_grouped:
    message += "Сегодня задач нет 🎉\n"
else:
    for project, tasks in today_grouped.items():
        message += f"📂 {project}\n"
        for task in tasks:
            title = task.get("title", "(без названия)")
            assignee = get_assignee(task)
            if assignee:
                message += f"- {title} (Исполнитель: {assignee})\n"
            else:
                message += f"- {title}\n"
        message += "\n"

# просроченные задачи
if overdue_grouped:
    message += "⚠️ Просроченные задачи\n\n"
    for project, tasks in overdue_grouped.items():
        message += f"📂 {project}\n"
        for task in tasks:
            title = task.get("title", "(без названия)")
            due = task.get("dueDate") or task.get("date") or ""
            assignee = get_assignee(task)
            if assignee:
                message += f"- {title} ({due}) (Исполнитель: {assignee})\n"
            else:
                message += f"- {title} ({due})\n"
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
