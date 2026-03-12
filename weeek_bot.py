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
print("TOTAL TASKS:", len(tasks))

for t in tasks:
    print(
        t.get("title"),
        "| date:", t.get("date"),
        "| dueDate:", t.get("dueDate"),
        "| parentId:", t.get("parentId")
    )
projects = requests.get(projects_url, headers=headers).json()["projects"]

# карта проектов
project_map = {p["id"]: p["title"] for p in projects}

today = datetime.today().date()


def get_task_date(task):

    if task.get("dueDate"):
        return datetime.strptime(task["dueDate"], "%Y-%m-%d").date()

    if task.get("date"):
        return datetime.strptime(task["date"], "%d.%m.%Y").date()

    return None


# карта всех задач
task_map = {t["id"]: t for t in tasks}

projects_tasks = {}

for task in tasks:

    task_date = get_task_date(task)

    # только задачи на сегодня
    if task_date != today:
        continue

    parent_id = task.get("parentId")

    if parent_id and parent_id in task_map:

        parent = task_map[parent_id]

        project_id = parent.get("projectId")
        project_name = project_map.get(project_id, "Без проекта")

        projects_tasks.setdefault(project_name, {}).setdefault(parent["title"], []).append({
            "title": task["title"],
            "id": task["id"]
        })

    else:

        project_id = task.get("projectId")
        project_name = project_map.get(project_id, "Без проекта")

        projects_tasks.setdefault(project_name, {}).setdefault(task["title"], [])


message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

keyboard = []

if not projects_tasks:

    message += "Нет задач"

else:

    for project, parents in projects_tasks.items():

        message += f"📂 {project}\n"

        for parent, subs in parents.items():

            message += f"• {parent}\n"

            for sub in subs:

                message += f"   • {sub['title']}\n"

                keyboard.append([
                    {
                        "text": f"Открыть: {sub['title']}",
                        "url": f"https://app.weeek.net/ws/1/task/{sub['id']}"
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

print("Telegram response:")
print(response.text)
