import os
import requests
import json

WEEEK_TOKEN = os.getenv("WEEEK_TOKEN")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

headers = {"Authorization": f"Bearer {WEEEK_TOKEN}"}

for url, params in [
    ("https://api.weeek.net/public/v1/workspace/members", {}),
    ("https://api.weeek.net/public/v1/workspace/members", {"workspaceId": WORKSPACE_ID}),
    ("https://api.weeek.net/public/v1/tm/members", {}),
    ("https://api.weeek.net/public/v1/tm/members", {"workspaceId": WORKSPACE_ID}),
]:
    r = requests.get(url, headers=headers, params=params)
    print(f"\n{url} params={params} → {r.status_code}")
    print(r.text[:400])
