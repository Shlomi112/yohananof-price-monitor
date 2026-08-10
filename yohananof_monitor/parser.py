"""Parsers for the official price-transparency XML schema (PriceFull / PromoFull).

Field names below were taken directly from a real Yohananof PriceFull/PromoFull
dump for store 046 (Mishor Adumim), not from documentation.
"""

import xml.etree.ElementTree as ET


def parse_price_file(xml_bytes):
    """Return {item_code: {"name": ..., "price": float}}."""
    root = ET.fromstring(xml_bytes)
    items = {}
    for item in root.find("Items") or []:
        code = item.findtext("ItemCode")
        if not code:
            continue
        price_text = item.findtext("ItemPrice")
        try:
            price = float(price_text) if price_text else None
        except ValueError:
            price = None
        items[code] = {
            "name": (item.findtext("ItemName") or "").strip(),
            "price": price,
        }
    return items


def parse_promo_file(xml_bytes):
    """Return {promotion_id: {description, start, end, items: [{item_code, discounted_price, discount_rate}]}}."""
    root = ET.fromstring(xml_bytes)
    promos = {}
    for promo in root.find("Promotions") or []:
        promo_id = promo.findtext("PromotionID")
        if not promo_id:
            continue

        promo_items = []
        groups = promo.find("Groups")
        if groups is not None:
            for group in groups.findall("Group"):
                promo_items_el = group.find("PromotionItems")
                if promo_items_el is None:
                    continue
                for promo_item in promo_items_el.findall("PromotionItem"):
                    item_code = promo_item.findtext("ItemCode")
                    if not item_code:
                        continue
                    discounted_price_text = promo_item.findtext("DiscountedPrice")
                    discount_rate_text = promo_item.findtext("DiscountRate")
                    try:
                        discounted_price = (
                            float(discounted_price_text) if discounted_price_text else None
                        )
                    except ValueError:
                        discounted_price = None
                    try:
                        discount_rate = (
                            float(discount_rate_text) if discount_rate_text else None
                        )
                    except ValueError:
                        discount_rate = None
                    promo_items.append(
                        {
                            "item_code": item_code,
                            "discounted_price": discounted_price,
                            "discount_rate": discount_rate,
                        }
                    )

        promos[promo_id] = {
            "description": (promo.findtext("PromotionDescription") or "").strip(),
            "start": promo.findtext("PromotionStartDateTime"),
            "end": promo.findtext("PromotionEndDateTime"),
            "items": promo_items,
        }
    return promos
