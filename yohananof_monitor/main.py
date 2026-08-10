"""Fetch the latest promo/price dump for a configured store, diff it against
the last run, and alert (Telegram, or stdout if not configured) on anything
new, changed, or ended.

Usage:
    python -m yohananof_monitor.main
Meant to be run periodically (see README for Windows Task Scheduler setup).
"""

import sys

from . import config, emoji_map, ftp_client, notify_telegram, parser, snapshot

# Windows consoles often default to a Hebrew/Latin codepage (e.g. cp1255) that
# can't encode every character we print (Hebrew text mixed with emoji) -
# reconfigure stdout to UTF-8 so a print() never crashes before the alert is sent.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _item_label(item_code, price_map):
    info = price_map.get(item_code)
    if info and info["name"]:
        return info["name"]
    return f"פריט {item_code}"


def _format_promo_items(promo, price_map):
    lines = []
    for item in promo.get("items", []):
        name = _item_label(item["item_code"], price_map)
        price = item.get("discounted_price")
        price_str = f"{price:.2f}₪" if price is not None else "?"
        emoji = emoji_map.pick_emoji(name)
        lines.append(f"    - {emoji} {name}: {price_str}")
    return lines


def _promo_headline_emoji(promo, price_map):
    """Pick an emoji for a promo's headline: based on its first item's name
    if we have one, otherwise a guess from the promo's own description."""
    items = promo.get("items", [])
    if items:
        name = _item_label(items[0]["item_code"], price_map)
        return emoji_map.pick_emoji(name)
    return emoji_map.pick_emoji(promo.get("description", ""))


def run(chain=None, store_id=None):
    chain = chain or config.CHAIN
    store_id = store_id or config.STORE_ID

    price_file = ftp_client.latest_full_file(chain, "Price", store_id)
    promo_file = ftp_client.latest_full_file(chain, "Promo", store_id)

    if not promo_file:
        print(f"No promo file found for chain={chain} store={store_id}")
        return

    price_map = {}
    if price_file:
        price_map = parser.parse_price_file(ftp_client.download(chain, price_file))

    current_promos = parser.parse_promo_file(ftp_client.download(chain, promo_file))
    previous_promos = snapshot.load_previous(chain, store_id)

    new_promos, ended_promos, changed_promos = snapshot.diff_promos(
        previous_promos, current_promos
    )

    if not previous_promos:
        print(f"First run for {chain}/{store_id}: saved {len(current_promos)} promos, no alert sent.")
        snapshot.save_current(chain, store_id, current_promos)
        return

    if not (new_promos or ended_promos or changed_promos):
        print(f"No promo changes for {chain}/{store_id}.")
        snapshot.save_current(chain, store_id, current_promos)
        return

    lines = [f"\U0001f6d2 עדכון מבצעים - יוחננוף מישור אדומים\n"]

    if new_promos:
        lines.append(f"✨ מבצעים חדשים ({len(new_promos)}):")
        for _, promo in new_promos:
            emoji = _promo_headline_emoji(promo, price_map)
            lines.append(f"  • {emoji} {promo['description']}")
            lines.extend(_format_promo_items(promo, price_map))
        lines.append("")

    if changed_promos:
        lines.append(f"\U0001f504 מבצעים שהשתנו ({len(changed_promos)}):")
        for _, _old, new in changed_promos:
            emoji = _promo_headline_emoji(new, price_map)
            lines.append(f"  • {emoji} {new['description']}")
            lines.extend(_format_promo_items(new, price_map))
        lines.append("")

    if ended_promos:
        lines.append(f"❌ מבצעים שהסתיימו ({len(ended_promos)}):")
        for _, promo in ended_promos:
            emoji = _promo_headline_emoji(promo, price_map)
            lines.append(f"  • {emoji} {promo['description']}")
        lines.append("")

    message = "\n".join(lines).strip()
    notify_telegram.send(message)
    print(message)

    snapshot.save_current(chain, store_id, current_promos)


if __name__ == "__main__":
    run()
