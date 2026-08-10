"""CLI: find a branch's StoreID by (partial) name.

Usage:
    python find_store.py yohananof "מישור אדומים"
"""

import sys

from yohananof_monitor import stores

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    if len(sys.argv) != 3:
        print("usage: python find_store.py <chain> <branch name or part of it>")
        sys.exit(1)

    chain, query = sys.argv[1], sys.argv[2]
    matches = stores.find_stores(chain, query)
    if not matches:
        print(f"No branch matching {query!r} found for chain {chain!r}.")
        return

    for s in matches:
        print(f"StoreID={s['store_id']}\tName={s['name']}\tAddress={s['address']}")


if __name__ == "__main__":
    main()
