"""Persist promo snapshots per store and diff the current run against the last one."""

import json
import os

from . import config


def _snapshot_path(chain, store_id):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    return os.path.join(config.DATA_DIR, f"{chain}_{store_id}_promos.json")


def load_previous(chain, store_id):
    path = _snapshot_path(chain, store_id)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current(chain, store_id, promos):
    path = _snapshot_path(chain, store_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(promos, f, ensure_ascii=False, indent=2)


def diff_promos(previous, current):
    """Compare two {promotion_id: {...}} snapshots.

    Returns (new_promos, ended_promos, changed_promos) as lists of
    (promotion_id, promo_dict) / (promotion_id, old_dict, new_dict).
    """
    prev_ids = set(previous.keys())
    curr_ids = set(current.keys())

    new_promos = [(pid, current[pid]) for pid in sorted(curr_ids - prev_ids)]
    ended_promos = [(pid, previous[pid]) for pid in sorted(prev_ids - curr_ids)]

    changed_promos = []
    for pid in sorted(prev_ids & curr_ids):
        old, new = previous[pid], current[pid]
        old_prices = sorted(
            (i["item_code"], i["discounted_price"]) for i in old.get("items", [])
        )
        new_prices = sorted(
            (i["item_code"], i["discounted_price"]) for i in new.get("items", [])
        )
        if old_prices != new_prices or old.get("description") != new.get("description"):
            changed_promos.append((pid, old, new))

    return new_promos, ended_promos, changed_promos
