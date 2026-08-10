"""One-off demo: pull real current promos and send a sample to Telegram
(not a real diff alert - just so you can see the format)."""

import sys

from yohananof_monitor import config, ftp_client, notify_telegram, parser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

price_file = ftp_client.latest_full_file(config.CHAIN, "Price", config.STORE_ID)
promo_file = ftp_client.latest_full_file(config.CHAIN, "Promo", config.STORE_ID)

price_map = parser.parse_price_file(ftp_client.download(config.CHAIN, price_file))
promos = parser.parse_promo_file(ftp_client.download(config.CHAIN, promo_file))

sample = list(promos.items())[:5]

lines = ["\U0001f6d2 דוגמה - מבצעים פעילים כרגע ביוחננוף מישור אדומים\n(לא התראה אמיתית, רק הדגמה)\n"]
for promo_id, promo in sample:
    lines.append(f"• {promo['description']}")
    for item in promo["items"]:
        name = price_map.get(item["item_code"], {}).get("name", f"פריט {item['item_code']}")
        price = item["discounted_price"]
        price_str = f"{price:.2f}₪" if price is not None else "?"
        lines.append(f"    - {name}: {price_str}")

message = "\n".join(lines)
notify_telegram.send(message)
print(message)
