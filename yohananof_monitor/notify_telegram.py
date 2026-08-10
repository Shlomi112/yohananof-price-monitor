"""Send alerts to Telegram via the Bot API (requests, no SDK needed)."""

import requests

from . import config


def send(text):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[telegram disabled - set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID]")
        return

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=15,
    )
    response.raise_for_status()
