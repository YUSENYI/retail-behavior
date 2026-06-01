# Quickstart: 商品零售用户行为分析系统

## Goal

Validate that the planned MVP can support trusted behavior analytics for retail operations before implementation tasks are generated.

## Prerequisites

- Read [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md), and [data-model.md](./data-model.md).
- Review [contracts/openapi.yaml](./contracts/openapi.yaml) with backend and frontend owners.
- Prepare a validation dataset containing:
  - A complete visit -> browse -> click -> cart -> order -> payment journey.
  - Duplicate, delayed, invalid, and out-of-order behavior events.
  - Anonymous visitor behavior that later links to a known user.
  - Paid, failed, cancelled, and refunded order/payment examples.
  - At least two roles with different data scopes.

## MVP Validation Flow

1. Ingest the behavior event sample through the behavior ingestion contract.
2. Confirm duplicate events are marked duplicate and are not counted twice.
3. Query behavior details with time, product, user/visitor, session, behavior type, and channel filters.
4. Query a user journey and verify that visit, browse, click, cart, order, and payment events appear in chronological order.
5. Query behavior summary metrics and verify visits, clicks, browse duration, source distribution, and search keyword results.
6. Query the conversion funnel and verify browse-to-click, click-to-cart, cart-to-order, and order-to-payment stages.
7. Query product heat rankings and verify browse, click, cart, favorite, purchase, and conversion rankings.
8. Query essential reports and verify metric units, active filters, freshness timestamp, and empty/loading/error expectations.
9. Repeat report and export requests with each role and verify access denial, masking, and audit logs.
10. Force an invalid metric sample and verify that negative counts, negative amounts, and rates outside 0% to 100% are quarantined.

## Constitution Gate Checks

- Data accuracy: all accepted validation events are counted exactly once.
- Traceability: at least one complete payment can be traced back to the original visit and source channel.
- Permission: out-of-scope users cannot view or export restricted reports.
- Privacy: phone, email, address, and payment identifiers are masked by default.
- Audit: login, query, export, permission change, report access, alert handling, and sensitive data access are recorded.
- Freshness: core dashboard responses expose `freshnessAt` and meet the 5-minute target during normal operation.
- Usability: dashboard views show current filters, metric units,口径 version, empty state, loading state, error state, and delayed state.

## Recommended Delivery Order

1. P1 behavior event ingestion, behavior details, journey tracing, permissions, masking, audit.
2. P1 behavior summary, conversion funnel, product heat, essential reports.
3. P2 user profiles, segments, and purchase intent.
4. P3 alerts, recommendation analysis, advanced exports, and operations-effect reports.

## Exit Criteria Before `/speckit-tasks`

- `plan.md` has no unresolved constitution gate violations.
- `research.md` records decisions for architecture, storage, idempotency, refresh, permissions, recommendations, and testing.
- `data-model.md` includes validation rules for all high-risk entities.
- `contracts/openapi.yaml` covers P1 APIs and representative P2/P3 interfaces.
- `AGENTS.md` points contributors to the current plan.
