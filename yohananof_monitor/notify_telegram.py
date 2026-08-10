"""Send alerts to Telegram via the Bot API (requests, no SDK needed)."""

import requests

from . import config

# Telegram's hard limit is 4096 chars/message; leave headroom for the
# "(part X/Y)" suffix we add when a report has to be split.
_MAX_LEN = 4000


def _chunk_by_lines(text, max_len):
    """Split text into <= max_len chunks, only breaking on line boundaries."""
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > max_len and current:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks or [""]


def _send_one(text):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={"chat_id": config.TELEGRAM_CHAT_ID, "text": text},
        timeout=15,
    )
    response.raise_for_status()


def send(text):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[telegram disabled - set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID]")
        return

    chunks = _chunk_by_lines(text, _MAX_LEN)
    for i, chunk in enumerate(chunks, start=1):
        if len(chunks) > 1:
            chunk = f"{chunk}\n\n(חלק {i}/{len(chunks)})"
        _send_one(chunk)
