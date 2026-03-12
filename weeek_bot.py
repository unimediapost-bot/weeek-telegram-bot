import os
import requests
import json

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

headers = {"Authorization": f"Bearer {WEEEK_TOKEN}"}

for url in [
    "https://api.weeek.net/public/v1/workspace/members",
    "https://api.weeek.net/public/v1/workspace/users",
    "https://api.weeek.net/public/v1/users",
]:
    r = requests.get(url, headers=headers, params={"workspaceId": WORKSPACE_ID})
    print(f"\n{url} → {r.status_code}")
    print(r.text[:500])
