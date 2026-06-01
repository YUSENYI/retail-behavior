from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AnalysisFilters:
    start_time: datetime | None = None
    end_time: datetime | None = None
    product_id: str | None = None
    user_id: str | None = None
    visitor_id: str | None = None
    session_id: str | None = None
    channel_id: str | None = None
    event_type: str | None = None
    segment_id: str | None = None
    intent_level: str | None = None

    def matches(self, event: object) -> bool:
        for name in ["product_id", "user_id", "visitor_id", "session_id", "channel_id", "event_type"]:
            expected = getattr(self, name)
            if expected is not None and getattr(event, name, None) != expected:
                return False
        occurred_at = getattr(event, "occurred_at", None)
        if self.start_time is not None and occurred_at is not None and occurred_at < self.start_time:
            return False
        if self.end_time is not None and occurred_at is not None and occurred_at > self.end_time:
            return False
        return True
