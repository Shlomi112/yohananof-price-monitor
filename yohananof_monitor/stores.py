"""Look up a chain's StoreID by branch name (e.g. to find a new branch)."""

import xml.etree.ElementTree as ET

from . import ftp_client


def list_stores(chain):
    """Return [{store_id, name, address}] for every branch of a chain."""
    names = ftp_client.list_files(chain, "*stores*")
    store_file = sorted(names)[-1] if names else None
    if not store_file:
        raise RuntimeError(f"No Stores file found for chain {chain}")

    root = ET.fromstring(ftp_client.download(chain, store_file))
    stores = []
    for store in root.iter("Store"):
        stores.append(
            {
                "store_id": store.findtext("StoreID"),
                "name": (store.findtext("StoreName") or "").strip(),
                "address": (store.findtext("Address") or "").strip(),
            }
        )
    return stores


def find_stores(chain, query):
    """Case-insensitive substring search over branch name/address."""
    query = query.strip()
    return [
        s
        for s in list_stores(chain)
        if query in s["name"] or query in s["address"]
    ]
