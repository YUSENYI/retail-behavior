from __future__ import annotations

from dataclasses import dataclass

from domain.enums import MetricUnit


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    key: str
    name: str
    unit: MetricUnit
    version: str = "v1"


METRIC_DEFINITIONS = {
    "visits": MetricDefinition("visits", "Visits", MetricUnit.COUNT),
    "clicks": MetricDefinition("clicks", "Clicks", MetricUnit.COUNT),
    "browse_duration": MetricDefinition("browse_duration", "Browse Duration", MetricUnit.SECONDS),
    "cart_adds": MetricDefinition("cart_adds", "Cart Additions", MetricUnit.COUNT),
    "orders": MetricDefinition("orders", "Orders", MetricUnit.COUNT),
    "payments": MetricDefinition("payments", "Payments", MetricUnit.COUNT),
    "sales_amount": MetricDefinition("sales_amount", "Sales Amount", MetricUnit.AMOUNT),
    "conversion_rate": MetricDefinition("conversion_rate", "Conversion Rate", MetricUnit.PERCENT),
}
