# Implementation Plan: 商品零售用户行为分析系统

**Branch**: `001-retail-behavior-analytics` | **Date**: 2026-05-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-retail-behavior-analytics/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

建设一个面向零售运营和分析人员的内部 Web 应用，支持用户行为采集、行为指标分析、转化漏斗、商品热度、画像分群、预警、推荐分析、购买意向识别和报表统计。首版以 5 人团队可交付的 MVP 为边界，优先实现行为采集与明细追踪、核心分析、漏斗、商品热度、权限、脱敏、审计和基础报表；P2/P3 能力按模块增量交付。

技术方案采用前后端分离的 Web 应用：后端提供行为事件接入、指标查询、权限审计和报表接口；前端提供筛选、图表、漏斗、路径和报表视图；数据层以可追溯的行为事件表、指标快照和报表快照为核心，保证幂等采集、延迟数据处理、指标口径版本化和敏感信息默认脱敏。

## Technical Context

**Language/Version**: Python 3.12+ for backend services; TypeScript 5.x for frontend.

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy, Alembic, React, ECharts, pytest, Playwright.

**Storage**: MySQL 8.0+ as primary transactional and analytics store with indexed/partitioned behavior events and summary tables; Redis for short-lived freshness markers, locks, and cache; managed file/object storage for authorized exports.

**Testing**: pytest for backend unit/integration tests; OpenAPI contract tests; Playwright for end-to-end dashboard and permission flows; frontend component tests for chart/filter states.

**Target Platform**: Browser-based internal operations application and backend service deployed on Linux/container infrastructure.

**Project Type**: Web application with backend API and frontend dashboard.

**Performance Goals**: Core dashboard metrics refresh within 5 minutes during normal operations; common filtered analysis views respond within 3 seconds at p95; report exports for up to 100,000 rows complete or enter a trackable queued state within 2 minutes; alert detection runs within 10 minutes of eligible source data.

**Constraints**: Behavior ingestion MUST be idempotent; event paths MUST be traceable from visit to payment; role and data-scope checks MUST protect every report, export, alert, profile, and segment view; sensitive fields MUST be masked by default; metric values MUST reject negative counts/amounts and rates outside 0% to 100%; MVP MUST remain feasible for a 5-person team.

**Scale/Scope**: Initial planning target is up to 100,000 active users, 100,000 products, 10 million behavior events per month, 5 primary roles, and roughly 12-16 operational screens across P1-P3 modules.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Data accuracy and idempotency**: PASS. `BehaviorEvent.event_id` plus source, type, object, subject, and occurred time provide deduplication. Ingestion records duplicate, invalid, delayed, and quarantined states. Metric snapshots store calculation window,口径 version, deduplication rule, late-arrival policy, and reconciliation status.
- **End-to-end traceability**: PASS. User/visitor, session, product, order, payment, channel, and timestamp relationships are defined in [data-model.md](./data-model.md). Journey and funnel contracts expose supporting event ids, stage order, source channel, and refresh time.
- **Permission and data protection**: PASS. Roles are administrator, operations manager, analyst, customer-service viewer, and read-only viewer. Contracts require authorization on dashboard, report, export, alert, profile, segment, and recommendation endpoints. Sensitive user fields are masked by default and all sensitive reads/exports are audited.
- **Real-time indicators and anomaly constraints**: PASS. Metric snapshots and quickstart validation require 5-minute freshness for visits, clicks, carts, orders, sales, and conversion. Non-negative numeric constraints and 0%-100% rate bounds are enforced at metric validation and report publication boundaries; invalid snapshots are quarantined.
- **Usable analysis experience**: PASS. Frontend scope includes dashboard filters for time, product, user, channel, segment, behavior type, and intent; chart states for loading, empty, delayed, and error; visible metric units, active filters,口径 version, and freshness timestamp.

Post-design re-check: PASS. Phase 1 artifacts define the data model, contracts, and quickstart checks needed to verify every constitution gate before `/speckit-tasks`.

## Project Structure

### Documentation (this feature)

```text
specs/001-retail-behavior-analytics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   ├── analytics/
│   ├── domain/
│   ├── jobs/
│   ├── models/
│   ├── reports/
│   ├── security/
│   └── services/
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── state/
│   └── test/
└── tests/
    ├── e2e/
    └── visual/

shared/
└── contracts/
```

**Structure Decision**: Use a two-app web structure because the feature needs a browser dashboard, backend event/analytics APIs, scheduled metric refresh, audit logging, and contract testing. Shared contracts hold generated or reviewed API schemas without coupling frontend and backend source trees.

## Complexity Tracking

No constitution violations are accepted for this plan.
