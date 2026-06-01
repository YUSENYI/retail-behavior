from __future__ import annotations

from domain.common import utcnow


class ReportService:
    def generate(self, report_type: str, filters: dict[str, object], items: list[object] | None = None) -> dict[str, object]:
        return {
            "reportId": f"{report_type}-{int(utcnow().timestamp())}",
            "reportType": report_type,
            "filters": filters,
            "items": items or [],
            "status": "ready",
            "sensitiveDataState": "masked",
            "freshnessAt": utcnow().isoformat(),
        }
