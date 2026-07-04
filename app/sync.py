import json
import os
import time
from datetime import datetime, timezone

import requests

APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
USER_ID = os.environ["DISCORD_USER_ID"]
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
INTERVAL_SECONDS = int(os.environ.get("SYNC_INTERVAL_SECONDS", "300"))

WIDGET_DATA_PATH = "/app/widget_data.json"

API_URL = (
    f"https://discord.com/api/v9/applications/{APPLICATION_ID}"
    f"/users/{USER_ID}/identities/0/profile"
)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bot {BOT_TOKEN}",
}


def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{timestamp}] {message}", flush=True)


def load_widget_data() -> dict:
    with open(WIDGET_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sync_once() -> None:
    payload = load_widget_data()
    response = requests.patch(API_URL, headers=HEADERS, json=payload, timeout=10)
    if response.ok:
        log(f"sync OK (status={response.status_code})")
    else:
        log(f"sync FAILED (status={response.status_code}): {response.text}")


def main() -> None:
    log(f"discord-widget-sync started (interval={INTERVAL_SECONDS}s)")
    while True:
        try:
            sync_once()
        except Exception as e:
            log(f"sync ERROR: {e}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
