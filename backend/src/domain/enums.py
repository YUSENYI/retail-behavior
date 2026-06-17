from __future__ import annotations

from enum import StrEnum


class EventType(StrEnum):
    BROWSE = "browse"
    CLICK = "click"
    SEARCH = "search"
    FAVORITE = "favorite"
    CART_ADD = "cart_add"
    ORDER_SUBMIT = "order_submit"
    PAYMENT_ATTEMPT = "payment_attempt"
    PAYMENT_SUCCESS = "payment_success"


class IdempotencyState(StrEnum):
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"
    INVALID = "invalid"
    DELAYED = "delayed"
    QUARANTINED = "quarantined"


class Role(StrEnum):
    ADMINISTRATOR = "administrator"
    OPERATIONS_MANAGER = "operations_manager"
    ANALYST = "analyst"
    CUSTOMER_SERVICE_VIEWER = "customer_service_viewer"
    READ_ONLY_VIEWER = "read_only_viewer"


class DataScope(StrEnum):
    ALL = "all"
    ASSIGNED_CHANNEL = "assigned_channel"
    ASSIGNED_STORE = "assigned_store"
    ASSIGNED_SEGMENT = "assigned_segment"
    OWN_REPORTS = "own_reports"
    NONE = "none"


class AlertStatus(StrEnum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class AlertType(StrEnum):
    LOW_ACTIVITY = "low_activity"
    CHURN_RISK = "churn_risk"
    CONVERSION_ANOMALY = "conversion_anomaly"
    BEHAVIOR_DATA_ANOMALY = "behavior_data_anomaly"


class MetricUnit(StrEnum):
    COUNT = "count"
    AMOUNT = "amount"
    PERCENT = "percent"
    SECONDS = "seconds"
    RANK = "rank"


class ValidationState(StrEnum):
    VALID = "valid"
    QUARANTINED = "quarantined"
    SUPERSEDED = "superseded"


class ReportType(StrEnum):
    BEHAVIOR_DETAIL = "behavior_detail"
    PRODUCT_ANALYSIS = "product_analysis"
    FUNNEL = "funnel"
    USER_PROFILE = "user_profile"
    USER_SEGMENT = "user_segment"
    SALES_CONVERSION = "sales_conversion"
    OPERATION_EFFECT = "operation_effect"


class AlertSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
