from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from domain.enums import IdempotencyState
from security.audit import audit_recorder
from security.auth import Principal
from services.behavior_event_repository import BehaviorEventRecord, BehaviorEventRepository, repository


class BehaviorIngestionService:
    def __init__(self, repo: BehaviorEventRepository = repository) -> None:
        self.repo = repo

    def ingest_batch(self, events: list[dict[str, Any]], principal: Principal | None = None) -> dict[str, Any]:
        results: list[dict[str, str | None]] = []
        counts: Counter[str] = Counter()
        for raw in events:
            record = BehaviorEventRecord(
                event_id=str(raw.get("eventId") or raw.get("event_id") or ""),
                source_system=str(raw.get("sourceSystem") or raw.get("source_system") or "unknown"),
                event_type=str(raw.get("eventType") or raw.get("event_type") or ""),
                user_id=raw.get("userId") or raw.get("user_id"),
                visitor_id=raw.get("visitorId") or raw.get("visitor_id"),
                session_id=str(raw.get("sessionId") or raw.get("session_id") or ""),
                product_id=raw.get("productId") or raw.get("product_id"),
                order_id=raw.get("orderId") or raw.get("order_id"),
                payment_id=raw.get("paymentId") or raw.get("payment_id"),
                channel_id=str(raw.get("channelId") or raw.get("channel_id") or ""),
                search_keyword=raw.get("searchKeyword") or raw.get("search_keyword"),
                occurred_at=self._parse_time(raw.get("occurredAt") or raw.get("occurred_at")),
                metadata=raw.get("metadata") or {},
            )
            stored = self.repo.ingest(record)
            counts[stored.idempotency_state.value] += 1
            results.append(
                {
                    "eventId": stored.event_id,
                    "state": stored.idempotency_state.value,
                    "reason": stored.exclusion_reason,
                }
            )
        if principal is not None:
            audit_recorder.log(principal, "create", "behavior_event", result="success")
        return {
            "acceptedCount": counts[IdempotencyState.ACCEPTED.value],
            "duplicateCount": counts[IdempotencyState.DUPLICATE.value],
            "invalidCount": counts[IdempotencyState.INVALID.value],
            "delayedCount": counts[IdempotencyState.DELAYED.value],
            "quarantinedCount": counts[IdempotencyState.QUARANTINED.value],
            "results": results,
        }

    @staticmethod
    def _parse_time(value: object) -> datetime:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=UTC)
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        return datetime.min.replace(tzinfo=UTC)
