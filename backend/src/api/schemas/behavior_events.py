from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BehaviorEventInput(BaseModel):
    eventId: str
    sourceSystem: str = "web"
    eventType: str
    userId: str | None = None
    visitorId: str | None = None
    sessionId: str
    productId: str | None = None
    orderId: str | None = None
    paymentId: str | None = None
    channelId: str
    searchKeyword: str | None = None
    occurredAt: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class BehaviorEventBatchRequest(BaseModel):
    events: list[BehaviorEventInput] = Field(min_length=1, max_length=1000)


class IngestionResult(BaseModel):
    acceptedCount: int
    duplicateCount: int
    invalidCount: int
    delayedCount: int
    quarantinedCount: int
    results: list[dict[str, str | None]]
