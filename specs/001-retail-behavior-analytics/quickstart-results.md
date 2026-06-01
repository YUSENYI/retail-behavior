# Quickstart Results

**Date**: 2026-05-28

## Validation Summary

- Behavior fixture includes a complete browse -> click -> cart -> order -> payment path.
- Duplicate payment event is marked duplicate and not counted as accepted.
- Invalid behavior event is marked invalid and excluded from accepted metrics.
- Journey tracing sorts accepted events chronologically.
- Core metric, funnel, and product heat services return bounded values.
- Permission, masking, export denial, and audit paths are covered by backend tests.

## Notes

The implementation uses MySQL configuration for deployment and in-memory service objects for fast local tests. Database migrations and ORM models are present for MySQL-backed persistence.
