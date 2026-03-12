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

project_map = {p["id"]: p["title"] for p in projects}

today = datetime.today().date()

# функция получения даты задачи
def get_task_date(task):

    if task.get("dueDate"):
        return datetime.strptime(task["dueDate"], "%Y-%m-%d").date()

    if task.get("date"):
        return datetime.strptime(task["date"], "%d.%m.%Y").date()

    return None


# структура parent -> children
children = {}

for t in tasks:

    parent = t.get("parentId")

    if parent:
        children.setdefault(parent, []).append(t)


projects_tasks = {}

for task in tasks:

    # только родительские задачи
    if task.get("parentId"):
        continue

    task_date = get_task_date(task)

    if task_date != today:
        continue

    project_id = task.get("projectId")
    project_name = project_map.get(project_id, "Без проекта")

    projects_tasks.setdefault(project_name, []).append(task)


message = "Доброе утро!\n\n📅 Задачи на сегодня\n\n"

keyboard = []

if not projects_tasks:
    message += "Нет задач"

else:

    for project, parent_tasks in projects_tasks.items():

        message += f"📂 {project}\n"

        for parent in parent_tasks:

            message += f"• {parent['title']}\n"

            keyboard.append([
                {
                    "text": f"Открыть: {parent['title']}",
                    "url": f"https://app.weeek.net/ws/1/task/{parent['id']}"
                }
            ])

            if parent["id"] in children:

                for sub in children[parent["id"]]:

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

print(response.text)
