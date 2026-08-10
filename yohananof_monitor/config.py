"""Configuration for the price monitor.

The chain publishes its price-transparency files on the shared "Cerberus"
FTPS portal (url.retail.publishedprices.co.il). Each chain has its own
username on that portal and an empty password. To add another chain that
uses the same portal, add a row to CHAINS below with its FTP username and
chain id (both are public - visible in the chain's own transparency page).
"""

import os


def _load_dotenv():
    """Tiny .env loader (no python-dotenv dependency) - doesn't override real env vars."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

FTP_HOST = "url.retail.publishedprices.co.il"

CHAINS = {
    "yohananof": {
        "ftp_username": "yohananof",
        "chain_id": "7290803800003",
    },
}

CHAIN = os.environ.get("PRICE_MONITOR_CHAIN", "yohananof")

# StoreID for Yohananof "מישור אדומים" (found via the Stores file, see stores.py).
# 046 = the store itself, 146 = its pickup point ("פיק אפ").
STORE_ID = os.environ.get("PRICE_MONITOR_STORE_ID", "046")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
