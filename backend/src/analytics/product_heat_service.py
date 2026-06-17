from __future__ import annotations

from collections import Counter
from datetime import datetime
from math import exp

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
        counts = _heat_scores(events) if rank_by in {"heat", "heat_score"} else _count_events(events, event_type)
        browse_counts = _count_events(events, "browse")
        purchase_counts = _count_events(events, "payment_success")
        items = []
        for idx, (product_id, value) in enumerate(counts.most_common(), start=1):
            conversion = 0 if browse_counts[product_id] == 0 else (purchase_counts[product_id] / browse_counts[product_id]) * 100
            item = {
                "productId": product_id,
                "productName": product_names.get(product_id, product_id),
                "rank": idx,
                "value": round(value, 2) if isinstance(value, float) else value,
                "unit": "score" if rank_by in {"heat", "heat_score"} else "count",
                "conversionRate": round(min(conversion, 100), 2),
            }
            if rank_by in {"heat", "heat_score"}:
                item["algorithmVersion"] = "weighted-decay-v2"
                item["browseCount"] = browse_counts[product_id]
                item["purchaseCount"] = purchase_counts[product_id]
            items.append(item)
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


def _heat_scores(events: list[BehaviorEventRecord]) -> Counter[str]:
    weights = {
        "browse": 1,
        "click": 2,
        "favorite": 3,
        "cart_add": 5,
        "order_submit": 8,
        "payment_success": 12,
    }
    now = utcnow().replace(tzinfo=None)
    scores: Counter[str] = Counter()
    browse_counts = _count_events(events, "browse")
    purchase_counts = _count_events(events, "payment_success")
    for event in events:
        if not event.product_id:
            continue
        age_days = max((now - _timestamp(event.occurred_at)).total_seconds() / 86400, 0)
        decay = exp(-age_days / 14)
        scores[event.product_id] += weights.get(event.event_type, 0) * decay
    for product_id, browse_count in browse_counts.items():
        conversion = 0 if browse_count == 0 else purchase_counts[product_id] / browse_count
        scores[product_id] += min(conversion, 1) * 20
    return scores


def _timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return datetime.min
