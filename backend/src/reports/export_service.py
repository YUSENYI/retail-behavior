from __future__ import annotations

from security.audit import audit_recorder
from security.auth import Principal, assert_allowed


class ExportService:
    def create_export(self, principal: Principal, report_type: str, filters: dict[str, object], reason: str | None = None) -> dict[str, object]:
        assert_allowed(principal, "export", "export", str(filters.get("channelId") or ""))
        audit_recorder.log(principal, "export", "report", report_type, reason=reason)
        return {
            "reportId": f"export-{report_type}",
            "reportType": report_type,
            "filters": filters,
            "status": "queued",
            "sensitiveDataState": "masked",
            "exportUri": None,
        }
