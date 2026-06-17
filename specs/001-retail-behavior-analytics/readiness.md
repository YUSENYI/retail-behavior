# Readiness Review

## Constitution Gates

- Data accuracy and idempotency: implemented through event identity, duplicate state, invalid state, and accepted-event metrics.
- Traceability: implemented through user, visitor, session, channel, product, order, payment, and chronological journey services.
- Permission and data protection: implemented through role/data-scope checks, default masking helpers, export denial, and audit records.
- Real-time indicators and anomaly constraints: implemented through metric freshness helpers, bounded metric validation, and refresh job entrypoints.
- Usable analysis experience: implemented through frontend filters, freshness badge, states, and analysis pages.

## Remaining Hardening Before Production

- Connect services to MySQL persistence instead of in-memory repositories for live traffic.
- Add real authentication integration.
- Replace placeholder frontend tables/charts with production ECharts visualizations.
- Add export storage implementation for generated files.
