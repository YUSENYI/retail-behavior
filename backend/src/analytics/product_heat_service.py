from __future__ import annotations

from collections import Counter

from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord


RANK_EVENT_MAP = {
    "browse": "browse",
    "click": "click",
    "cart_add": "cart_add",
    "favorite": "favorite",
    "payment": "payment_success",
    "purchase": "payment_success",
    "sales": "payment_success",
}


class ProductHeatService:
    def rank(self, events: list[BehaviorEventRecord], rank_by: str = "browse") -> dict[str, object]:
        event_type = RANK_EVENT_MAP.get(rank_by, rank_by)
        product_names = _product_names(events)
        counts = _count_events(events, event_type)
        browse_counts = _count_events(events, "browse")
        purchase_counts = _count_events(events, "payment_success")
        items = []
        for idx, (product_id, value) in enumerate(counts.most_common(), start=1):
            conversion = 0 if browse_counts[product_id] == 0 else (purchase_counts[product_id] / browse_counts[product_id]) * 100
            items.append(
                {
                    "productId": product_id,
                    "productName": product_names.get(product_id, product_id),
                    "rank": idx,
                    "value": value,
                    "unit": "count",
                    "conversionRate": round(min(conversion, 100), 2),
                }
            )
        return {"items": items, "freshnessAt": utcnow().isoformat()}


def _count_events(events: list[BehaviorEventRecord], event_type: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for event in events:
        if not event.product_id or event.event_type != event_type:
            continue
        counts[event.product_id] += _sale_quantity(event) if event_type == "payment_success" else 1
    return counts


def _product_names(events: list[BehaviorEventRecord]) -> dict[str, str]:
    names: dict[str, str] = {}
    for event in events:
        if not event.product_id or event.product_id in names:
            continue
        name = event.metadata.get("productName") or event.metadata.get("product_name")
        names[event.product_id] = str(name or event.product_id)
    return names


def _sale_quantity(event: BehaviorEventRecord) -> int:
    try:
        quantity = int(event.metadata.get("quantity", 1))
    except (TypeError, ValueError):
        return 1
    return quantity if quantity > 0 else 1
