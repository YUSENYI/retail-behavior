# Research: 商品零售用户行为分析系统

## Decision: Use a backend API plus frontend dashboard architecture

**Rationale**: The feature combines event ingestion, metric computation, permissions, reports, and interactive dashboard analysis. Separating backend API and frontend dashboard lets a 5-person team divide work cleanly while preserving contract-driven development and independent testing.

**Alternatives considered**:
- Monolithic server-rendered app: simpler deployment, but weaker fit for rich chart interactions and dashboard state.
- Off-the-shelf BI-only solution: faster reporting, but insufficient for behavior ingestion, idempotency, journey tracing, alert workflow, and masking/audit rules.

## Decision: Use Python/FastAPI for backend and TypeScript/React for frontend

**Rationale**: Python supports rapid delivery of analytics, segmentation, recommendation rules, and data validation. FastAPI and Pydantic align well with explicit request/response contracts. React with TypeScript supports complex filters, charts, and dashboard state with manageable team ownership.

**Alternatives considered**:
- Java/Spring Boot with Vue: strong enterprise choice, but higher ceremony for a small MVP team.
- Node-only full stack: simple language sharing, but less convenient for later analytics and recommendation scoring.

## Decision: Store raw behavior events and summary snapshots in MySQL

**Rationale**: The MVP needs trustworthy traceability more than large-scale stream processing. MySQL 8.0+ partitioning, unique indexes, check constraints, generated columns where useful, and summary tables can support the initial 10 million events/month target while aligning with the project's database choice. Metric snapshots retain口径 version, source window, freshness, and validation state.

**Alternatives considered**:
- ClickHouse: excellent for high-volume analytics, but adds operational complexity before the MVP proves scale.
- Kafka plus stream processor: useful for larger real-time pipelines, but not required for a 5-minute freshness target.
- Warehouse-only model: good for historical reporting, but too slow and indirect for near-real-time dashboards and alerts.
- PostgreSQL: strong analytics-friendly relational option, but not selected because the project standard is MySQL.

## Decision: Make event ingestion idempotent and auditable from day one

**Rationale**: The constitution requires no duplicate or missing statistics. Every behavior event carries a stable event id and idempotency state. Duplicate, invalid, delayed, and quarantined events remain visible for reconciliation instead of disappearing silently.

**Alternatives considered**:
- Best-effort ingestion with periodic cleanup: simpler, but makes metric disputes hard to resolve.
- Overwrite latest event state only: loses evidence needed for troubleshooting and audit.

## Decision: Use scheduled incremental metric refresh for the MVP

**Rationale**: A 5-minute refresh target can be met with frequent incremental jobs that scan new accepted events, update metric snapshots, and publish freshness metadata. This avoids introducing a streaming platform before the team needs it.

**Alternatives considered**:
- Fully synchronous metric updates on every event: simpler for small volume, but risks slow ingestion and inconsistent complex metrics.
- Dedicated streaming engine: powerful but heavy for the MVP and 5-person delivery constraint.

## Decision: Enforce role/data-scope permissions, masking, and audit across all read and export flows

**Rationale**: The system exposes sensitive user behavior and profile data. Permissions must be enforced before data leaves backend services, not only in the UI. All report access, export attempts, permission changes, and sensitive reads create audit records.

**Alternatives considered**:
- UI-only permission hiding: easy to bypass and fails audit requirements.
- Separate report copies per role: duplicates logic and increases risk of口径 drift.

## Decision: Begin recommendation and purchase-intent analysis with explainable business rules

**Rationale**: The MVP and P2/P3 roadmap need useful, auditable recommendations without opaque models. Rule-based scoring from browsing, purchasing, similar-user overlap, profile tags, cart abandonment, and activity is explainable and easier to validate. More advanced models can replace or augment scores later.

**Alternatives considered**:
- Machine-learning-first recommendations: attractive long term, but needs more data science effort, evaluation data, and governance.
- Manual recommendations only: explainable but too labor-intensive and not scalable.

## Decision: Use contract, integration, and end-to-end tests as release gates

**Rationale**: The feature has high-risk cross-cutting behavior: idempotency, traceability, metric bounds, permissions, masking, audit, and dashboard states. Contract tests protect API behavior, integration tests protect event-to-metric correctness, and Playwright tests protect user workflows.

**Alternatives considered**:
- Unit tests only: insufficient for journey traceability and authorization flows.
- Manual QA only: too risky for duplicate counting, masking, exports, and alert state transitions.
