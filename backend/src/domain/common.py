from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(UTC)


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


class Page(BaseModel):
    items: list[Any]
    page: int
    page_size: int
    total: int


class TimeWindow(BaseModel):
    start_time: datetime
    end_time: datetime

    def contains(self, value: datetime) -> bool:
        return self.start_time <= value <= self.end_time
