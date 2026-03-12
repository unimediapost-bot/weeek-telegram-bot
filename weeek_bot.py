import requests
from datetime import date
import os

WEEEK_TOKEN = os.getenv("4e29aac5-2402-470e-be1d-d6d43429c4f5")
TELEGRAM_TOKEN = os.getenv("8209309373:AAFyzlm13TrY9k964CKu4kVA4Vcksh6_ALQ")
CHAT_ID = os.getenv("5274619421")

url = "https://api.weeek.net/public/v1/tm/tasks"

headers = {
    "Authorization": f"Bearer {WEEEK_TOKEN}"
}

response = requests.get(url, headers=headers)
data = response.json()

today = date.today().isoformat()

today_tasks = []
overdue_tasks = []

for task in data["data"]:

    title = task["title"]
    due = task.get("dueDate")

    if due == today:
        today_tasks.append(title)

    if due and due < today:
        overdue_tasks.append(title)

message = "Доброе утро!\n\n"

message += "📅 Задачи на сегодня\n"

if today_tasks:
    for t in today_tasks:
        message += f"• {t}\n"
else:
    message += "Нет задач\n"

message += "\n⚠️ Просроченные\n"

if overdue_tasks:
    for t in overdue_tasks:
        message += f"• {t}\n"
else:
    message += "Нет\n"

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message
}

requests.post(telegram_url, json=payload)
