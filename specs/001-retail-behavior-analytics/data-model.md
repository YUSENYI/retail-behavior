# Data Model: 商品零售用户行为分析系统

## Entity Overview

The model preserves raw event traceability, calculates governed metrics, and protects sensitive user data by default.

## Entities

### User

**Purpose**: Known retail customer or internal operator subject, depending on context.

**Fields**:
- `user_id`: stable unique identifier.
- `visitor_id`: optional anonymous identifier linked after login or order association.
- `display_name`: masked display name where required.
- `phone_masked`, `email_masked`, `address_masked`: default visible sensitive fields.
- `demographic_attributes`: age band, gender, region, or other allowed profile attributes.
- `created_at`, `updated_at`: lifecycle timestamps.
- `status`: active, inactive, deleted, or restricted.

**Validation**:
- Sensitive fields MUST be masked for non-authorized responses.
- A user can link to multiple sessions and behavior events.

### Visitor

**Purpose**: Anonymous actor before reliable user identification.

**Fields**:
- `visitor_id`: stable anonymous identifier.
- `first_seen_at`, `last_seen_at`: observed activity range.
- `linked_user_id`: optional user id after reliable association.
- `source_channel_id`: first known acquisition channel.

**Validation**:
- Visitor-to-user links MUST preserve original anonymous journey history.
- Link changes MUST be auditable.

### Session

**Purpose**: Continuous visit context for behavior paths.

**Fields**:
- `session_id`: unique session identifier.
- `user_id`, `visitor_id`: one or both identifiers.
- `channel_id`: source or entry channel.
- `started_at`, `ended_at`: session time window.
- `entry_url`, `exit_url`: optional navigation context.
- `device_context`: optional device or client category.

**Relationships**:
- One session has many behavior events.
- One session can include many products and funnel stages.

### BehaviorEvent

**Purpose**: Single observed behavior used for traceability and metrics.

**Fields**:
- `event_id`: globally unique idempotency key.
- `source_system`: origin of the event.
- `event_type`: browse, click, search, favorite, cart_add, order_submit, payment_attempt, payment_success.
- `user_id`, `visitor_id`, `session_id`: subject and path keys.
- `product_id`: required for product-specific behavior when applicable.
- `order_id`, `payment_id`: present for order and payment behavior.
- `channel_id`: source channel.
- `search_keyword`: present for search events.
- `occurred_at`: user-action time.
- `received_at`: ingestion time.
- `idempotency_state`: accepted, duplicate, invalid, delayed, or quarantined.
- `exclusion_reason`: reason for invalid or excluded events.
- `metadata`: bounded optional context.

**Validation**:
- `event_id` MUST be unique per source.
- `occurred_at` MUST be present and cannot be unreasonably far in the future.
- Product events MUST include `product_id`.
- Duplicate events MUST NOT affect metrics more than once.
- Invalid, delayed, or quarantined events MUST remain visible for reconciliation.

### Product

**Purpose**: Retail item being analyzed, ranked, purchased, or recommended.

**Fields**:
- `product_id`: unique identifier.
- `sku`, `name`, `category_id`, `brand`: product descriptors.
- `status`: active, inactive, removed, or unavailable.
- `list_price`, `current_price`: non-negative monetary values.
- `created_at`, `updated_at`: lifecycle timestamps.

**Relationships**:
- One product has many behavior events, orders, metric snapshots, and recommendation insights.

### Order

**Purpose**: Purchase order linked to funnel and sales conversion.

**Fields**:
- `order_id`: unique order identifier.
- `user_id`, `visitor_id`, `session_id`: buyer context.
- `status`: submitted, paid, cancelled, refunded, failed.
- `gross_amount`, `net_amount`: non-negative amounts.
- `submitted_at`, `paid_at`, `cancelled_at`, `refunded_at`: lifecycle timestamps.

**Validation**:
- Paid sales metrics count only paid orders unless a report explicitly uses another口径.
- Cancelled, failed, and refunded effects MUST be represented in metric reconciliation rules.

### Payment

**Purpose**: Payment attempt or success connected to conversion completion.

**Fields**:
- `payment_id`: unique payment identifier.
- `order_id`: linked order.
- `status`: attempted, succeeded, failed, refunded.
- `amount`: non-negative payment amount.
- `payment_time`: time of attempt or success.
- `payment_identifier_masked`: default visible payment identifier.

**Validation**:
- Payment success completes the order-to-payment funnel stage.
- Payment identifiers MUST be masked by default.

### Channel

**Purpose**: Acquisition or activity source.

**Fields**:
- `channel_id`: unique identifier.
- `name`: source name.
- `type`: campaign, search, recommendation, store, direct, social, other.
- `owner`: optional operations owner.
- `status`: active or inactive.

### MetricDefinition

**Purpose**: Governed口径 for a metric.

**Fields**:
- `metric_key`: visits, clicks, browse_duration, cart_adds, orders, payments, sales_amount, conversion_rate, retention_rate, churn_rate, etc.
- `name`, `description`, `unit`: business-readable definition.
- `deduplication_rule`: event identity rule used for the metric.
- `calculation_rule`: plain-language calculation.
- `valid_min`, `valid_max`: valid numeric bounds.
- `version`:口径 version.
- `effective_from`, `effective_to`: version lifecycle.

**Validation**:
- Count and amount metrics MUST have minimum 0.
- Rate metrics MUST be bounded between 0 and 100.

### MetricSnapshot

**Purpose**: Published metric value for dashboards and reports.

**Fields**:
- `snapshot_id`: unique identifier.
- `metric_key`, `metric_version`: metric definition reference.
- `scope_type`: global, product, channel, segment, user, or report.
- `scope_id`: optional scoped object id.
- `window_start`, `window_end`: statistics window.
- `value`: numeric metric value.
- `unit`: count, amount, percent, seconds, or rank.
- `freshness_at`: time source data was last included.
- `calculated_at`: calculation time.
- `validation_state`: valid, quarantined, or superseded.
- `source_event_count`: count of contributing accepted events.

**Validation**:
- Invalid bounds MUST set `validation_state` to quarantined and block publication.
- Every published snapshot MUST reference a metric definition version.

### FunnelStageSnapshot

**Purpose**: Conversion funnel stage and transition values.

**Fields**:
- `funnel_id`: unique funnel calculation id.
- `stage`: browse, click, cart, order, payment.
- `window_start`, `window_end`: time window.
- `scope_type`, `scope_id`: optional product/channel/segment scope.
- `entered_count`, `converted_count`, `dropoff_count`: non-negative counts.
- `conversion_rate`, `dropoff_rate`: percentages from 0 to 100.
- `freshness_at`: included data timestamp.

**Validation**:
- `entered_count` MUST be greater than or equal to converted and dropoff counts after口径 rules.
- Rates MUST remain between 0 and 100.

### UserProfile

**Purpose**: Analytical profile dimensions for a user.

**Fields**:
- `profile_id`, `user_id`: identifiers.
- `basic_attribute_tags`: allowed demographic or account tags.
- `consumption_level`: low, medium, high, very_high.
- `interest_tags`: product/category preferences.
- `activity_level`: low, medium, high.
- `value_grade`: low, medium, high, strategic.
- `updated_at`, `basis_window`: calculation metadata.

**Validation**:
- Profile updates MUST record the rule or source window.
- Sensitive input fields MUST not be exposed in profile responses.

### UserSegment

**Purpose**: Managed group of users.

**Fields**:
- `segment_id`: unique identifier.
- `segment_type`: high_value, potential, new_user, price_sensitive, silent, churn_risk.
- `name`, `description`: business label.
- `rule_description`: explainable membership rule.
- `member_count`: non-negative count.
- `last_calculated_at`: calculation timestamp.

**Relationships**:
- A segment has many `UserSegmentMembership` records.

### UserSegmentMembership

**Purpose**: Link between user and segment with reason.

**Fields**:
- `segment_id`, `user_id`: identifiers.
- `joined_at`, `left_at`: membership lifecycle.
- `reason`: primary membership basis.
- `score`: optional non-negative score.

### Alert

**Purpose**: Operational warning for behavior and conversion anomalies.

**Fields**:
- `alert_id`: unique identifier.
- `alert_type`: low_activity, churn_risk, conversion_anomaly, behavior_data_anomaly.
- `severity`: low, medium, high, critical.
- `status`: new, acknowledged, processing, resolved, ignored.
- `scope_type`, `scope_id`: affected user, product, channel, segment, or metric.
- `trigger_reason`: explainable reason.
- `created_at`, `updated_at`, `resolved_at`: lifecycle timestamps.
- `owner_id`: responsible operator.

**State transitions**:
- new -> acknowledged -> processing -> resolved.
- new or acknowledged -> ignored.
- resolved and ignored are terminal unless a new alert is generated.

### RecommendationInsight

**Purpose**: Explainable recommendation analysis result.

**Fields**:
- `insight_id`: unique identifier.
- `target_type`: user or segment.
- `target_id`: user or segment id.
- `product_id`: recommended product.
- `basis_type`: browse_history, purchase_history, similar_users, user_profile.
- `reason`: business-readable explanation.
- `priority`: low, medium, high.
- `score`: 0 to 100.
- `generated_at`: generation time.

### PurchaseIntent

**Purpose**: User purchase-intent classification.

**Fields**:
- `intent_id`, `user_id`: identifiers.
- `intent_level`: high, medium, low, cart_unpaid.
- `related_product_id`: optional product.
- `basis`: behavior basis such as repeated browse, cart abandonment, recent purchase, or profile match.
- `score`: 0 to 100.
- `updated_at`: calculation time.

### Report

**Purpose**: Generated analysis view or export.

**Fields**:
- `report_id`: unique identifier.
- `report_type`: behavior_detail, product_analysis, funnel, user_profile, user_segment, sales_conversion, operation_effect.
- `filters`: time, product, user, channel, segment, behavior type, and intent filters.
- `created_by`, `created_at`: generation context.
- `status`: ready, queued, failed, expired.
- `export_uri`: optional export location.
- `sensitive_data_state`: masked, unmasked_authorized, or not_applicable.

**Validation**:
- Export generation MUST check role and data scope before creating output.
- Report filters MUST be recorded for audit and reproducibility.

### RolePermission

**Purpose**: Role and data-scope access control.

**Fields**:
- `role_id`: administrator, operations_manager, analyst, customer_service_viewer, read_only_viewer.
- `resource`: dashboard, behavior_event, journey, report, export, alert, profile, segment, recommendation, permission.
- `actions`: view, create, update, handle, export, manage.
- `data_scope`: all, assigned_channel, assigned_store, assigned_segment, own_reports, none.

### AuditLog

**Purpose**: Immutable audit record for security and traceability.

**Fields**:
- `audit_id`: unique identifier.
- `actor_id`, `actor_role`: operator context.
- `action`: login, query, export, permission_change, report_access, alert_handling, sensitive_data_access.
- `resource_type`, `resource_id`: affected object.
- `result`: success, denied, failed.
- `reason`: optional operator or system reason.
- `created_at`: event time.
- `request_context`: bounded client and filter context.

## Cross-Entity Validation Rules

- Every published metric or report MUST trace to accepted behavior events, source orders/payments, or a named metric definition.
- Duplicate, invalid, delayed, and quarantined events MUST not silently affect published dashboards.
- Counts and amounts MUST be non-negative.
- Rates MUST be between 0 and 100 inclusive.
- Sensitive fields MUST be masked unless the role, resource, action, and data scope allow unmasked access.
- Every export and sensitive read MUST produce an audit log.
- Role permission changes MUST be effective for the next request and recorded in audit logs.
