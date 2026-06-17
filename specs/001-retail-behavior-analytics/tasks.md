# Tasks: 商品零售用户行为分析系统

**Input**: Design documents from `/specs/001-retail-behavior-analytics/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Required for behavior collection, metric calculation, traceability, permissions, masking, audit logging, real-time refresh, anomaly validation, and all OpenAPI contracts.

**Organization**: Tasks are grouped by user story so each story can be implemented, tested, and demonstrated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps the task to the user story phase, for example [US1].
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the backend, frontend, shared contract, and validation scaffolding used by all stories.

- [X] T001 Create backend source and test directories in `backend/src/`, `backend/tests/unit/`, `backend/tests/integration/`, and `backend/tests/contract/`
- [X] T002 Create frontend source and test directories in `frontend/src/`, `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/services/`, `frontend/tests/e2e/`, and `frontend/tests/visual/`
- [X] T003 Create shared contract directory and copy OpenAPI planning contract into `shared/contracts/openapi.yaml`
- [X] T004 Initialize backend Python project metadata and dependencies in `backend/pyproject.toml`
- [X] T005 Initialize frontend TypeScript project metadata and dependencies in `frontend/package.json`
- [X] T006 [P] Add backend lint, type-check, and test configuration in `backend/pyproject.toml`
- [X] T007 [P] Add frontend lint, type-check, test, and Playwright configuration in `frontend/package.json`
- [X] T008 [P] Add local service configuration for MySQL, Redis, backend, and frontend in `docker-compose.yml`
- [X] T009 [P] Add environment example values for database, Redis, auth, masking, export storage, and freshness limits in `.env.example`
- [X] T010 [P] Create validation fixture dataset with complete journey, duplicates, delayed events, anonymous visitor link, and payment outcomes in `backend/tests/fixtures/retail_behavior_sample.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared domain, persistence, security, auditing, API shell, frontend shell, and validation primitives that every story relies on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T011 Configure database engine, session management, and migration environment in `backend/src/models/database.py` and `backend/alembic/env.py`
- [X] T012 [P] Define shared enum values for event types, idempotency states, roles, report types, alert status, metric units, and validation states in `backend/src/domain/enums.py`
- [X] T013 [P] Define base timestamp, identifier, and pagination schemas in `backend/src/domain/common.py`
- [X] T014 Create initial migration for users, visitors, sessions, products, orders, payments, channels, role permissions, and audit logs in `backend/alembic/versions/001_foundation.py`
- [X] T015 [P] Implement user, visitor, session, product, channel, order, and payment ORM models in `backend/src/models/foundation.py`
- [X] T016 [P] Implement role permission and audit log ORM models in `backend/src/models/security.py`
- [X] T017 [P] Implement authentication principal extraction and role/data-scope policy evaluation in `backend/src/security/auth.py`
- [X] T018 [P] Implement sensitive-field masking utilities for users, payments, profiles, reports, and exports in `backend/src/security/masking.py`
- [X] T019 [P] Implement audit logging service for login, query, export, permission change, report access, alert handling, and sensitive data access in `backend/src/security/audit.py`
- [X] T020 Implement FastAPI application factory, router registration, error handling, and request context middleware in `backend/src/api/app.py`
- [X] T021 [P] Implement freshness metadata and bounded metric value validation helpers in `backend/src/analytics/validation.py`
- [X] T022 [P] Implement reusable filter parsing for time, product, user, visitor, session, channel, segment, behavior type, and purchase intent in `backend/src/api/filters.py`
- [X] T023 [P] Add unit tests for role/data-scope authorization and denied access audit logging in `backend/tests/unit/test_authorization.py`
- [X] T024 [P] Add unit tests for masking phone, email, address, payment identifier, profile, and export fields in `backend/tests/unit/test_masking.py`
- [X] T025 [P] Add unit tests for non-negative counts, non-negative amounts, and 0-to-100 percent validation in `backend/tests/unit/test_metric_validation.py`
- [X] T026 [P] Create frontend application shell, routing, auth state, and shared layout in `frontend/src/App.tsx` and `frontend/src/state/auth.ts`
- [X] T027 [P] Create reusable dashboard filter, freshness badge, loading, empty, delayed, and error state components in `frontend/src/components/analytics/`
- [X] T028 [P] Create generated API client wrapper from `shared/contracts/openapi.yaml` in `frontend/src/services/apiClient.ts`

**Checkpoint**: Foundation ready. User story work can now proceed by priority.

---

## Phase 3: User Story 1 - 管理用户行为采集与明细追踪 (Priority: P1)

**Goal**: Collect behavior events exactly once, query behavior details, and trace user/visitor journeys from visit to payment.

**Independent Test**: Ingest the validation fixture, confirm duplicates are excluded, query filtered behavior details, and display one complete chronological journey with permission-scoped data.

### Tests for User Story 1

- [X] T029 [P] [US1] Add OpenAPI contract tests for POST `/events/behavior` in `backend/tests/contract/test_behavior_ingestion_contract.py`
- [X] T030 [P] [US1] Add OpenAPI contract tests for GET `/behavior/events` and GET `/behavior/journeys/{subjectId}` in `backend/tests/contract/test_behavior_query_contract.py`
- [X] T031 [P] [US1] Add integration tests for duplicate, invalid, delayed, and out-of-order behavior events in `backend/tests/integration/test_behavior_ingestion_accuracy.py`
- [X] T032 [P] [US1] Add integration tests for anonymous visitor linking and visit-to-payment journey ordering in `backend/tests/integration/test_journey_traceability.py`
- [X] T033 [P] [US1] Add permission, masking, and audit tests for behavior detail and journey access in `backend/tests/integration/test_behavior_access_audit.py`
- [X] T034 [P] [US1] Add Playwright journey and behavior detail workflow tests in `frontend/tests/e2e/behavior_journey.spec.ts`

### Implementation for User Story 1

- [X] T035 [P] [US1] Create behavior event ORM model and migration in `backend/src/models/behavior_event.py` and `backend/alembic/versions/002_behavior_events.py`
- [X] T036 [P] [US1] Create behavior event request and response schemas in `backend/src/api/schemas/behavior_events.py`
- [X] T037 [US1] Implement idempotent behavior ingestion repository with accepted, duplicate, invalid, delayed, and quarantined states in `backend/src/services/behavior_event_repository.py`
- [X] T038 [US1] Implement behavior ingestion service with event identity, validation, visitor linking hooks, and audit context in `backend/src/services/behavior_ingestion_service.py`
- [X] T039 [US1] Implement behavior detail query service with filters, pagination, masking, and permission scoping in `backend/src/services/behavior_query_service.py`
- [X] T040 [US1] Implement journey tracing service that orders visit, browse, click, search, favorite, cart, order, and payment events in `backend/src/services/journey_service.py`
- [X] T041 [US1] Add behavior ingestion and query API routes in `backend/src/api/routes/behavior.py`
- [X] T042 [P] [US1] Implement frontend behavior API service methods in `frontend/src/services/behaviorApi.ts`
- [X] T043 [P] [US1] Build behavior detail page with time, product, user, visitor, session, behavior type, and channel filters in `frontend/src/pages/BehaviorEventsPage.tsx`
- [X] T044 [P] [US1] Build chronological journey timeline component with freshness and idempotency states in `frontend/src/components/analytics/JourneyTimeline.tsx`
- [X] T045 [US1] Wire behavior detail and journey routes into frontend navigation in `frontend/src/App.tsx`

**Checkpoint**: US1 can be validated independently with behavior ingestion, duplicate handling, detail filters, journey tracing, permission checks, masking, and audit logs.

---

## Phase 4: User Story 2 - 分析行为指标、商品热度和转化漏斗 (Priority: P1)

**Goal**: Provide behavior summary metrics, conversion funnel stages, drop-off analysis, and product heat rankings with bounded values and visible freshness.

**Independent Test**: Use the validation dataset to verify visits, clicks, browse duration, source distribution, search keywords, funnel rates, drop-off stages, and product heat rankings.

### Tests for User Story 2

- [X] T046 [P] [US2] Add OpenAPI contract tests for GET `/analytics/behavior-summary` in `backend/tests/contract/test_behavior_summary_contract.py`
- [X] T047 [P] [US2] Add OpenAPI contract tests for GET `/analytics/funnel` and GET `/analytics/product-heat` in `backend/tests/contract/test_funnel_product_heat_contract.py`
- [X] T048 [P] [US2] Add integration tests for visit count, click count, browse duration, visit source, and search keyword metrics in `backend/tests/integration/test_behavior_metrics.py`
- [X] T049 [P] [US2] Add integration tests for funnel conversion, drop-off, cancelled orders, failed payments, and 0-to-100 rate bounds in `backend/tests/integration/test_funnel_metrics.py`
- [X] T050 [P] [US2] Add integration tests for product heat rankings and non-negative count/amount validation in `backend/tests/integration/test_product_heat_metrics.py`
- [X] T051 [P] [US2] Add Playwright dashboard, funnel, and product heat workflow tests in `frontend/tests/e2e/analytics_dashboard.spec.ts`

### Implementation for User Story 2

- [X] T052 [P] [US2] Create metric definition, metric snapshot, and funnel snapshot models and migration in `backend/src/models/metrics.py` and `backend/alembic/versions/003_metrics.py`
- [X] T053 [P] [US2] Create analytics response schemas for metrics, funnel stages, and product heat rankings in `backend/src/api/schemas/analytics.py`
- [X] T054 [US2] Implement metric definition seed data for visits, clicks, browse duration, cart additions, orders, payments, sales, and conversion rates in `backend/src/analytics/metric_definitions.py`
- [X] T055 [US2] Implement incremental metric refresh job with freshness metadata and late-event reconciliation in `backend/src/jobs/metric_refresh_job.py`
- [X] T056 [US2] Implement behavior summary service for visits, clicks, browse duration, source distribution, and search keywords in `backend/src/analytics/behavior_summary_service.py`
- [X] T057 [US2] Implement conversion funnel service for browse-to-click, click-to-cart, cart-to-order, order-to-payment, and drop-off analysis in `backend/src/analytics/funnel_service.py`
- [X] T058 [US2] Implement product heat service for browse, click, cart, favorite, purchase, and conversion rankings in `backend/src/analytics/product_heat_service.py`
- [X] T059 [US2] Add analytics API routes in `backend/src/api/routes/analytics.py`
- [X] T060 [P] [US2] Implement frontend analytics API service methods in `frontend/src/services/analyticsApi.ts`
- [X] T061 [P] [US2] Build behavior summary dashboard with metric cards, trend charts, source chart, and search keyword table in `frontend/src/pages/BehaviorSummaryPage.tsx`
- [X] T062 [P] [US2] Build conversion funnel page with stage counts, rates, drop-off highlighting, and current filters in `frontend/src/pages/FunnelAnalysisPage.tsx`
- [X] T063 [P] [US2] Build product heat ranking page with rank mode switch, table, and freshness display in `frontend/src/pages/ProductHeatPage.tsx`
- [X] T064 [US2] Wire analytics pages into frontend navigation and shared filter state in `frontend/src/App.tsx`

**Checkpoint**: MVP is usable after US1 and US2: behavior collection, journey tracing, core analytics, funnel, product heat, permissions, masking, audit, and freshness are demonstrable.

---

## Phase 5: User Story 3 - 建立用户画像、分群和购买意向识别 (Priority: P2)

**Goal**: Maintain user profile dimensions, segment users by business rules, and classify purchase intent including cart-unpaid users.

**Independent Test**: Apply known user, purchase, and behavior samples to verify profile tags, segment membership, and high/medium/low/cart-unpaid purchase intent labels.

### Tests for User Story 3

- [X] T065 [P] [US3] Add OpenAPI contract tests for GET `/profiles/{userId}` in `backend/tests/contract/test_profile_contract.py`
- [X] T066 [P] [US3] Add OpenAPI contract tests for GET `/segments`, GET `/segments/{segmentId}/users`, and GET `/purchase-intent/users` in `backend/tests/contract/test_segments_intent_contract.py`
- [X] T067 [P] [US3] Add integration tests for profile dimension calculation and masked profile responses in `backend/tests/integration/test_user_profiles.py`
- [X] T068 [P] [US3] Add integration tests for high-value, potential, new, price-sensitive, silent, and churn-risk segment rules in `backend/tests/integration/test_user_segments.py`
- [X] T069 [P] [US3] Add integration tests for high, medium, low, and cart-unpaid purchase intent classification in `backend/tests/integration/test_purchase_intent.py`
- [X] T070 [P] [US3] Add Playwright profile, segment, and purchase-intent workflow tests in `frontend/tests/e2e/profile_segment_intent.spec.ts`

### Implementation for User Story 3

- [X] T071 [P] [US3] Create user profile, segment, segment membership, and purchase intent models and migration in `backend/src/models/profiles.py` and `backend/alembic/versions/004_profiles_segments.py`
- [X] T072 [P] [US3] Create profile, segment, and purchase-intent schemas in `backend/src/api/schemas/profiles.py`
- [X] T073 [US3] Implement user profile calculation service for basic attributes, consumption ability, interests, activity level, and value grade in `backend/src/services/profile_service.py`
- [X] T074 [US3] Implement segment rule service for high-value, potential, new, price-sensitive, silent, and churn-risk users in `backend/src/services/segment_service.py`
- [X] T075 [US3] Implement purchase-intent service for high, medium, low, and cart-unpaid users with explainable basis in `backend/src/services/purchase_intent_service.py`
- [X] T076 [US3] Add profile, segment, and purchase-intent API routes in `backend/src/api/routes/profiles.py`
- [X] T077 [P] [US3] Implement frontend profile, segment, and purchase-intent API methods in `frontend/src/services/profileApi.ts`
- [X] T078 [P] [US3] Build user profile page with profile dimensions, masked user fields, and rule basis in `frontend/src/pages/UserProfilePage.tsx`
- [X] T079 [P] [US3] Build user segments page with segment filters, member counts, and membership reasons in `frontend/src/pages/UserSegmentsPage.tsx`
- [X] T080 [P] [US3] Build purchase intent page with intent-level filters and cart-unpaid identification in `frontend/src/pages/PurchaseIntentPage.tsx`
- [X] T081 [US3] Wire profile, segment, and purchase-intent routes into frontend navigation in `frontend/src/App.tsx`

**Checkpoint**: US3 can be validated independently using profile, segment, and purchase-intent fixtures without requiring alert or recommendation workflows.

---

## Phase 6: User Story 4 - 监控预警与推荐分析 (Priority: P3)

**Goal**: Generate and manage low-activity, churn-risk, conversion-anomaly, and behavior-data-anomaly alerts, and show explainable recommendation analysis.

**Independent Test**: Trigger alert and recommendation samples, verify alert status transitions, audit logs, anomaly reasons, recommendation basis, and role-scoped visibility.

### Tests for User Story 4

- [X] T082 [P] [US4] Add OpenAPI contract tests for GET `/alerts` and PATCH `/alerts/{alertId}` in `backend/tests/contract/test_alerts_contract.py`
- [X] T083 [P] [US4] Add OpenAPI contract tests for GET `/recommendations/analysis` in `backend/tests/contract/test_recommendations_contract.py`
- [X] T084 [P] [US4] Add integration tests for low-activity, churn-risk, conversion-anomaly, and behavior-data-anomaly alert triggers in `backend/tests/integration/test_alert_rules.py`
- [X] T085 [P] [US4] Add integration tests for alert status transitions, denied handling, and audit records in `backend/tests/integration/test_alert_workflow.py`
- [X] T086 [P] [US4] Add integration tests for browse-history, purchase-history, similar-user, and profile-based recommendation reasons in `backend/tests/integration/test_recommendation_analysis.py`
- [X] T087 [P] [US4] Add Playwright alert and recommendation workflow tests in `frontend/tests/e2e/alerts_recommendations.spec.ts`

### Implementation for User Story 4

- [X] T088 [P] [US4] Create alert and recommendation insight models and migration in `backend/src/models/alerts_recommendations.py` and `backend/alembic/versions/005_alerts_recommendations.py`
- [X] T089 [P] [US4] Create alert and recommendation schemas in `backend/src/api/schemas/alerts_recommendations.py`
- [X] T090 [US4] Implement alert rule service for low activity, churn risk, conversion anomaly, and behavior data anomaly in `backend/src/services/alert_rule_service.py`
- [X] T091 [US4] Implement alert workflow service for acknowledge, processing, resolved, and ignored transitions with audit logging in `backend/src/services/alert_workflow_service.py`
- [X] T092 [US4] Implement recommendation analysis service with browse, purchase, similar-user, and profile bases in `backend/src/services/recommendation_service.py`
- [X] T093 [US4] Implement scheduled alert and recommendation refresh jobs in `backend/src/jobs/alert_recommendation_job.py`
- [X] T094 [US4] Add alert and recommendation API routes in `backend/src/api/routes/alerts_recommendations.py`
- [X] T095 [P] [US4] Implement frontend alert and recommendation API methods in `frontend/src/services/alertRecommendationApi.ts`
- [X] T096 [P] [US4] Build alerts page with severity, trigger reason, scope, status transition controls, and delayed state in `frontend/src/pages/AlertsPage.tsx`
- [X] T097 [P] [US4] Build recommendation analysis page with recommendation basis, priority, and target filters in `frontend/src/pages/RecommendationAnalysisPage.tsx`
- [X] T098 [US4] Wire alert and recommendation routes into frontend navigation in `frontend/src/App.tsx`

**Checkpoint**: US4 can be validated independently once US1/US2 data and US3 profiles are available; alerts and recommendations remain explainable and auditable.

---

## Phase 7: User Story 5 - 生成运营报表并按权限查看 (Priority: P3)

**Goal**: Provide behavior detail, product analysis, funnel, profile, segment, sales conversion, and operations-effect reports with authorized export, masking, and audit.

**Independent Test**: Use multiple roles to view and export reports, verify scoped data, denied exports, masked sensitive fields, freshness, filter reproduction, and audit log records.

### Tests for User Story 5

- [X] T099 [P] [US5] Add OpenAPI contract tests for GET `/reports` and POST `/reports/{reportType}/exports` in `backend/tests/contract/test_reports_contract.py`
- [X] T100 [P] [US5] Add OpenAPI contract tests for GET `/audit-logs` in `backend/tests/contract/test_audit_logs_contract.py`
- [X] T101 [P] [US5] Add integration tests for behavior detail, product analysis, funnel, profile, segment, sales conversion, and operations-effect report generation in `backend/tests/integration/test_reports.py`
- [X] T102 [P] [US5] Add integration tests for export authorization denial, sensitive field masking, and audit records in `backend/tests/integration/test_report_export_security.py`
- [X] T103 [P] [US5] Add Playwright report filtering, export denial, masked report, and audit visibility tests in `frontend/tests/e2e/reports_audit.spec.ts`

### Implementation for User Story 5

- [X] T104 [P] [US5] Create report model and migration in `backend/src/models/reports.py` and `backend/alembic/versions/006_reports.py`
- [X] T105 [P] [US5] Create report, export, and audit log response schemas in `backend/src/api/schemas/reports.py`
- [X] T106 [US5] Implement report generation service for behavior detail, product analysis, funnel, profile, segment, sales conversion, and operations-effect reports in `backend/src/reports/report_service.py`
- [X] T107 [US5] Implement export service with role/data-scope checks, masking, queued status, and audit logging in `backend/src/reports/export_service.py`
- [X] T108 [US5] Implement audit log query service with administrator-scoped filtering in `backend/src/security/audit_query_service.py`
- [X] T109 [US5] Add report, export, and audit log API routes in `backend/src/api/routes/reports.py`
- [X] T110 [P] [US5] Implement frontend report and audit API methods in `frontend/src/services/reportApi.ts`
- [X] T111 [P] [US5] Build reports page with report type selector, filters, metric units, freshness, and export actions in `frontend/src/pages/ReportsPage.tsx`
- [X] T112 [P] [US5] Build audit log page with action, actor, resource, result, and time filters in `frontend/src/pages/AuditLogsPage.tsx`
- [X] T113 [US5] Wire report and audit routes into frontend navigation in `frontend/src/App.tsx`

**Checkpoint**: US5 can be validated independently using role-specific report and export flows with audit evidence.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Harden the full feature, validate quickstart, and prepare the system for implementation review.

- [X] T114 [P] Add generated API contract synchronization check for `shared/contracts/openapi.yaml` and `specs/001-retail-behavior-analytics/contracts/openapi.yaml` in `backend/tests/contract/test_openapi_sync.py`
- [X] T115 [P] Add accessibility and visual regression coverage for dashboard, funnel, report, and alert states in `frontend/tests/visual/analytics_visual.spec.ts`
- [X] T116 [P] Add performance tests for 10 million monthly event assumptions, 3-second filtered views, and 5-minute metric freshness in `backend/tests/integration/test_performance_targets.py`
- [X] T117 [P] Add security regression tests for unauthorized routes, unmasked data leakage, and export scope bypass in `backend/tests/integration/test_security_regression.py`
- [X] T118 Update operational documentation for roles, metric definitions, masking, audit logs, alert handling, and exports in `docs/retail_behavior_analytics.md`
- [X] T119 Run and document quickstart MVP validation results in `specs/001-retail-behavior-analytics/quickstart-results.md`
- [X] T120 Review all routes, pages, and tests against constitution gates and record final readiness notes in `specs/001-retail-behavior-analytics/readiness.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **US1 (Phase 3)**: Depends on Foundational; first P1 increment.
- **US2 (Phase 4)**: Depends on Foundational and benefits from US1 accepted events; completes MVP with core analytics.
- **US3 (Phase 5)**: Depends on Foundational and US1/US2 data services for profile and segment inputs.
- **US4 (Phase 6)**: Depends on US1/US2 for behavior and metrics; recommendation rules also benefit from US3 profiles.
- **US5 (Phase 7)**: Depends on relevant report source modules; can start report shell after Foundational, then fill report types as US1-US4 land.
- **Polish**: Depends on all desired stories for the release.

### User Story Dependencies

- **US1**: Independent after Foundational.
- **US2**: Can be developed after Foundational using fixture events; production-quality validation depends on US1 ingestion.
- **US3**: Can be developed with fixtures after Foundational; richer validation depends on US1/US2 behavior and metric outputs.
- **US4**: Alerts can start with metrics fixtures after US2; recommendations use US3 profile outputs when available.
- **US5**: Report framework can start after Foundational; each report type depends on the source story it summarizes.

### Within Each User Story

- Contract and integration tests must be written and fail before implementation.
- Models and migrations precede services.
- Services precede API routes.
- API routes precede frontend service methods.
- Frontend service methods precede pages and E2E completion.
- Story checkpoint must pass before considering the story complete.

---

## Parallel Execution Examples

### User Story 1

```bash
Task: "T029 contract tests in backend/tests/contract/test_behavior_ingestion_contract.py"
Task: "T030 contract tests in backend/tests/contract/test_behavior_query_contract.py"
Task: "T034 Playwright workflow in frontend/tests/e2e/behavior_journey.spec.ts"
Task: "T036 schemas in backend/src/api/schemas/behavior_events.py"
```

### User Story 2

```bash
Task: "T046 contract tests in backend/tests/contract/test_behavior_summary_contract.py"
Task: "T047 contract tests in backend/tests/contract/test_funnel_product_heat_contract.py"
Task: "T061 dashboard page in frontend/src/pages/BehaviorSummaryPage.tsx"
Task: "T062 funnel page in frontend/src/pages/FunnelAnalysisPage.tsx"
Task: "T063 product heat page in frontend/src/pages/ProductHeatPage.tsx"
```

### User Story 3

```bash
Task: "T065 profile contract tests in backend/tests/contract/test_profile_contract.py"
Task: "T066 segment and intent contract tests in backend/tests/contract/test_segments_intent_contract.py"
Task: "T078 profile page in frontend/src/pages/UserProfilePage.tsx"
Task: "T079 segment page in frontend/src/pages/UserSegmentsPage.tsx"
Task: "T080 purchase intent page in frontend/src/pages/PurchaseIntentPage.tsx"
```

### User Story 4

```bash
Task: "T082 alert contract tests in backend/tests/contract/test_alerts_contract.py"
Task: "T083 recommendation contract tests in backend/tests/contract/test_recommendations_contract.py"
Task: "T096 alerts page in frontend/src/pages/AlertsPage.tsx"
Task: "T097 recommendation page in frontend/src/pages/RecommendationAnalysisPage.tsx"
```

### User Story 5

```bash
Task: "T099 report contract tests in backend/tests/contract/test_reports_contract.py"
Task: "T100 audit contract tests in backend/tests/contract/test_audit_logs_contract.py"
Task: "T111 reports page in frontend/src/pages/ReportsPage.tsx"
Task: "T112 audit logs page in frontend/src/pages/AuditLogsPage.tsx"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 behavior ingestion, behavior details, journey tracing, permissions, masking, and audit.
3. Complete US2 behavior summary, funnel analysis, product heat, metric validation, and freshness.
4. Stop and validate the quickstart MVP flow in `specs/001-retail-behavior-analytics/quickstart.md`.

### Incremental Delivery

1. Add US3 profiles, segments, and purchase intent after the P1 MVP is stable.
2. Add US4 alerts and recommendation analysis after metrics and profile inputs are available.
3. Add US5 reports and exports progressively, starting with P1 report types and expanding as P2/P3 modules land.
4. Run final polish tasks before release.

### 5-Person Team Strategy

1. Developer A: backend foundation, database migrations, ingestion, and metrics.
2. Developer B: backend analytics, profiles, alerts, reports, and exports.
3. Developer C: frontend app shell, behavior, analytics, funnel, and product heat pages.
4. Developer D: frontend profile, segment, intent, alert, recommendation, report, and audit pages.
5. Developer E: contract, integration, E2E, security, performance, and quickstart validation tests.

---

## Notes

- Total tasks: 120.
- MVP scope: Phase 1, Phase 2, US1, and US2.
- [P] tasks can be run in parallel when their dependencies are satisfied.
- Tests for constitution-sensitive behavior are intentionally first in each story phase.
- Every story has an independent checkpoint and can be validated with fixtures.
