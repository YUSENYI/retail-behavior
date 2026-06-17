from __future__ import annotations

import json

from analytics.behavior_summary_service import BehaviorSummaryService
from analytics.funnel_service import FunnelService
from analytics.product_heat_service import ProductHeatService
from domain.common import utcnow
from models.database import SessionLocal, use_mysql_persistence
from models.reports import Report
from sqlalchemy import select


class ReportService:
    def generate(
        self,
        report_type: str,
        filters: dict[str, object],
        items: list[object] | None = None,
        created_by: str = "system",
    ) -> dict[str, object]:
        report = {
            "reportId": f"{report_type}-{int(utcnow().timestamp())}",
            "reportType": report_type,
            "filters": filters,
            "items": items or [],
            "summary": self._summary(report_type, items or []),
            "status": "ready",
            "sensitiveDataState": "masked",
            "algorithmVersion": "report-snapshot-v2",
            "freshnessAt": utcnow().isoformat(),
        }
        self._save_report(report, created_by)
        return report

    def list_reports(self, report_type: str | None = None) -> list[dict[str, object]]:
        if not use_mysql_persistence():
            return []
        statement = select(Report).order_by(Report.created_at.desc())
        if report_type:
            statement = statement.where(Report.report_type == report_type)
        with SessionLocal() as session:
            rows = session.scalars(statement).all()
            return [self._row_to_dict(row) for row in rows]

    def _save_report(self, report: dict[str, object], created_by: str) -> None:
        if not use_mysql_persistence():
            return
        now = utcnow().replace(tzinfo=None)
        with SessionLocal() as session:
            row = session.get(Report, str(report["reportId"]))
            if row is None:
                row = Report(
                    report_id=str(report["reportId"]),
                    report_type=str(report["reportType"]),
                    filters=json.dumps(report["filters"], ensure_ascii=False, default=str),
                    created_by=created_by,
                    created_at=now,
                    status=str(report["status"]),
                    export_uri=None,
                    sensitive_data_state=str(report["sensitiveDataState"]),
                    freshness_at=now,
                )
                session.add(row)
            session.commit()

    def _row_to_dict(self, row: Report) -> dict[str, object]:
        filters: dict[str, object] = {}
        if row.filters:
            loaded = json.loads(row.filters)
            if isinstance(loaded, dict):
                filters = loaded
        return {
            "reportId": row.report_id,
            "reportType": row.report_type,
            "filters": filters,
            "items": [],
            "summary": {},
            "status": row.status,
            "sensitiveDataState": row.sensitive_data_state,
            "algorithmVersion": "report-snapshot-v2",
            "freshnessAt": row.freshness_at.isoformat() if row.freshness_at else None,
            "createdBy": row.created_by,
            "createdAt": row.created_at.isoformat(),
            "exportUri": row.export_uri,
        }

    def _summary(self, report_type: str, items: list[object]) -> dict[str, object]:
        behavior_items = [item for item in items if hasattr(item, "event_type")]
        if behavior_items:
            return {
                "behaviorSummary": BehaviorSummaryService().summarize(behavior_items)["metrics"],
                "funnel": FunnelService().analyze(behavior_items)["stages"],
                "topProducts": ProductHeatService().rank(behavior_items, "heat")["items"][:5],
            }
        return {
            "reportType": report_type,
            "itemCount": len(items),
            "insight": "Report snapshot generated with masked sensitive fields.",
        }
