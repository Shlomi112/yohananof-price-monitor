"""Answer Telegram messages like "יש מבצע על כנפיים?" or a shopping list
(one product per line), using the same price/promo data already fetched
this run - no extra download, no extra API calls to the price portal.

Only replies to the configured owner chat (config.TELEGRAM_CHAT_ID); messages
from anyone else are acknowledged (so we don't keep re-fetching them) but
never answered.
"""

import json
import os

import requests

from . import config, emoji_map, notify_telegram

_OFFSET_PATH = os.path.join(config.DATA_DIR, "telegram_offset.json")

_FILLER_WORDS = {
    "יש",
    "האם",
    "מבצע",
    "מבצעים",
    "על",
    "לי",
    "בבקשה",
    "מה",
    "תבדוק",
    "בדוק",
    "אפשר",
    "תראה",
    "לך",
    "אולי",
    "כרגע",
    "היום",
    "גם",
}
_PUNCTUATION = "?!.,;:\"'()"


def _load_offset():
    if not os.path.exists(_OFFSET_PATH):
        return 0
    with open(_OFFSET_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("offset", 0)


def _save_offset(offset):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(_OFFSET_PATH, "w", encoding="utf-8") as f:
        json.dump({"offset": offset}, f)


def _get_updates(offset):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url, params={"offset": offset, "timeout": 0}, timeout=15)
    response.raise_for_status()
    return response.json().get("result", [])


def _extract_term(line):
    cleaned = line
    for ch in _PUNCTUATION:
        cleaned = cleaned.replace(ch, " ")
    words = [w for w in cleaned.split() if w not in _FILLER_WORDS]
    return " ".join(words).strip()


def _search(term, price_map, promos):
    matched_promos = []
    for promo in promos.values():
        haystacks = [promo.get("description", "")]
        for item in promo.get("items", []):
            info = price_map.get(item["item_code"])
            if info and info["name"]:
                haystacks.append(info["name"])
        if any(term in h for h in haystacks if h):
            matched_promos.append(promo)

    matched_items = []
    if not matched_promos:
        for info in price_map.values():
            if info["name"] and term in info["name"]:
                matched_items.append(info)
                if len(matched_items) >= 5:
                    break

    return matched_promos[:5], matched_items


def _format_result(term, matched_promos, matched_items, price_map):
    if matched_promos:
        lines = [f'🔎 מבצעים על "{term}":']
        for promo in matched_promos:
            items = promo.get("items", [])
            emoji = (
                emoji_map.pick_emoji(price_map.get(items[0]["item_code"], {}).get("name", ""))
                if items
                else emoji_map.pick_emoji(promo.get("description", ""))
            )
            lines.append(f"  • {emoji} {promo['description']}")

            # Bundle-type promos ("buy any of these 15 items, get 50% off")
            # can list dozens of items - show the ones matching the search
            # term first, cap the rest so one promo doesn't swamp the reply.
            def _matches_term(item):
                name = price_map.get(item["item_code"], {}).get("name") or ""
                return term in name

            sorted_items = sorted(items, key=lambda i: not _matches_term(i))
            shown, remaining = sorted_items[:5], sorted_items[5:]
            for item in shown:
                info = price_map.get(item["item_code"], {})
                name = info.get("name") or f"פריט {item['item_code']}"
                price = item.get("discounted_price")
                price_str = f"{price:.2f}₪" if price is not None else "?"
                lines.append(f"      - {name}: {price_str}")
            if remaining:
                lines.append(f"      + עוד {len(remaining)} פריטים במבצע הזה")
        return lines

    if matched_items:
        lines = [f'לא נמצא מבצע על "{term}", אבל יש במחיר רגיל:']
        for info in matched_items:
            emoji = emoji_map.pick_emoji(info["name"])
            price = info.get("price")
            price_str = f"{price:.2f}₪" if price is not None else "?"
            lines.append(f"  {emoji} {info['name']}: {price_str}")
        return lines

    return [f'❌ לא מצאתי "{term}" בסניף מישור אדומים.']


def check_and_reply(price_map, promos):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return

    offset = _load_offset()
    updates = _get_updates(offset)
    if not updates:
        return

    max_update_id = offset - 1
    for update in updates:
        max_update_id = max(max_update_id, update["update_id"])
        message = update.get("message") or update.get("edited_message")
        if not message or "text" not in message:
            continue

        chat_id = str(message["chat"]["id"])
        if chat_id != str(config.TELEGRAM_CHAT_ID):
            continue  # not the owner - acknowledge (advance offset) but don't answer

        text = message["text"].strip()
        if not text or text.startswith("/"):
            continue

        reply_lines = []
        for line in text.splitlines():
            term = _extract_term(line)
            if not term:
                continue
            matched_promos, matched_items = _search(term, price_map, promos)
            reply_lines.extend(_format_result(term, matched_promos, matched_items, price_map))
            reply_lines.append("")

        if not reply_lines:
            reply_lines = ['לא הבנתי מה לחפש 🤔 נסה למשל: "יש מבצע על חלב?"']

        notify_telegram.send("\n".join(reply_lines).strip())

    _save_offset(max_update_id + 1)
