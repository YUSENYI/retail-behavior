from __future__ import annotations

import pytest

from analytics.validation import MetricValidationError, validate_metric_value
from domain.enums import MetricUnit, ValidationState


def test_non_negative_count_and_amount() -> None:
    assert validate_metric_value(0, MetricUnit.COUNT) == ValidationState.VALID
    assert validate_metric_value(12.5, MetricUnit.AMOUNT) == ValidationState.VALID
    with pytest.raises(MetricValidationError):
        validate_metric_value(-1, MetricUnit.COUNT)


def test_percent_bounds() -> None:
    assert validate_metric_value(100, MetricUnit.PERCENT) == ValidationState.VALID
    with pytest.raises(MetricValidationError):
        validate_metric_value(101, MetricUnit.PERCENT)
