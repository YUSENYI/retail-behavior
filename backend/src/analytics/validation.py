from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.common import utcnow
from domain.enums import MetricUnit, ValidationState


class MetricValidationError(ValueError):
    pass


@dataclass(slots=True)
class Freshness:
    freshness_at: datetime
    max_age_minutes: int = 5


def validate_metric_value(value: float, unit: MetricUnit) -> ValidationState:
    if unit in {MetricUnit.COUNT, MetricUnit.AMOUNT, MetricUnit.SECONDS, MetricUnit.RANK} and value < 0:
        raise MetricValidationError(f"{unit} cannot be negative")
    if unit == MetricUnit.PERCENT and not 0 <= value <= 100:
        raise MetricValidationError("percent metrics must be between 0 and 100")
    return ValidationState.VALID


def current_freshness() -> Freshness:
    return Freshness(freshness_at=utcnow())
