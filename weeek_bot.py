import os
import requests
import json

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

headers = {"Authorization": f"Bearer {WEEEK_TOKEN}"}

for url in [
    "https://api.weeek.net/public/v1/workspace",
    "https://api.weeek.net/public/v1/workspaces",
    "https://api.weeek.net/public/v1/workspace/info",
    "https://api.weeek.net/public/v1/workspace/team",
    "https://api.weeek.net/public/v1/team",
    "https://api.weeek.net/public/v1/user",
    "https://api.weeek.net/public/v1/users/me",
]:
    r = requests.get(url, headers=headers, params={"workspaceId": WORKSPACE_ID})
    print(f"{url} → {r.status_code} | {r.text[:200]}")
