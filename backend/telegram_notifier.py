import os
import requests


def get_chat_ids():
    raw = os.getenv("TELEGRAM_CHAT_IDS", "").strip()
    if not raw:
        return []

    return [chat_id.strip() for chat_id in raw.split(",") if chat_id.strip()]


def send_telegram_message(text: str) -> None:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_ids = get_chat_ids()

    if not telegram_bot_token or not chat_ids:
        return

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    for chat_id in chat_ids:
        try:
            requests.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                },
                timeout=5,
            )
        except Exception:
            pass