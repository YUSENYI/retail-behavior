from __future__ import annotations

import base64
import csv
import io
import os
from pathlib import Path
import re

from analytics.behavior_summary_service import BehaviorSummaryService
from analytics.funnel_service import FunnelService
from analytics.product_heat_service import ProductHeatService
from domain.common import utcnow
from domain.enums import ReportType
from security.audit import audit_recorder
from security.auth import PermissionDenied, Principal, assert_allowed
from security.masking import mask_identifier
from services.behavior_event_repository import BehaviorEventRecord, BehaviorEventRepository, repository


class ExportService:
    def __init__(
        self,
        repo: BehaviorEventRepository = repository,
        storage_path: str | os.PathLike[str] | None = None,
    ) -> None:
        self.repo = repo
        self.storage_path = Path(storage_path or os.getenv("EXPORT_STORAGE_PATH", "var/exports"))

    def create_export(
        self,
        principal: Principal,
        report_type: str,
        filters: dict[str, object],
        reason: str | None = None,
    ) -> dict[str, object]:
        scope_id = str(filters.get("channelId") or filters.get("channel_id") or "") or None
        try:
            assert_allowed(principal, "report", "export", scope_id)
        except PermissionDenied as exc:
            audit_recorder.log(
                principal,
                "export",
                "report",
                report_type,
                result="denied",
                reason=str(exc),
            )
            raise

        normalized_report_type = self._normalize_report_type(report_type)
        rows = self._report_rows(normalized_report_type, self._filtered_events(filters))
        csv_text = self._csv_text(normalized_report_type, rows)
        file_name = self._write_file(principal, normalized_report_type, csv_text)
        audit_recorder.log(principal, "export", "report", normalized_report_type, reason=reason)
        return {
            "reportId": f"export-{normalized_report_type}",
            "reportType": normalized_report_type,
            "filters": filters,
            "status": "ready",
            "sensitiveDataState": "masked",
            "exportUri": self._data_uri(csv_text),
            "fileName": file_name,
            "mimeType": "text/csv",
            "rowCount": len(rows),
        }

    def _filtered_events(self, filters: dict[str, object]) -> list[BehaviorEventRecord]:
        events = self.repo.accepted_events()
        channel_id = filters.get("channelId") or filters.get("channel_id")
        product_id = filters.get("productId") or filters.get("product_id")
        user_id = filters.get("userId") or filters.get("user_id")
        event_type = filters.get("eventType") or filters.get("event_type")
        if channel_id:
            events = [event for event in events if event.channel_id == str(channel_id)]
        if product_id:
            events = [event for event in events if event.product_id == str(product_id)]
        if user_id:
            events = [event for event in events if event.subject_id == str(user_id)]
        if event_type:
            events = [event for event in events if event.event_type == str(event_type)]
        return events

    def _report_rows(
        self,
        report_type: str,
        events: list[BehaviorEventRecord],
    ) -> list[dict[str, object]]:
        if report_type == ReportType.BEHAVIOR_DETAIL.value:
            return [self._behavior_row(event) for event in events]
        if report_type == ReportType.PRODUCT_ANALYSIS.value:
            return ProductHeatService().rank(events, "heat")["items"]  # type: ignore[return-value]
        if report_type == ReportType.FUNNEL.value:
            return FunnelService().analyze(events)["stages"]  # type: ignore[return-value]
        if report_type == ReportType.USER_PROFILE.value:
            return self._user_profile_rows(events)
        if report_type == ReportType.USER_SEGMENT.value:
            return self._user_segment_rows(events)
        if report_type == ReportType.SALES_CONVERSION.value:
            return self._sales_conversion_rows(events)
        return self._operation_effect_rows(events)

    def _behavior_row(self, event: BehaviorEventRecord) -> dict[str, object]:
        return {
            "事件ID": event.event_id,
            "行为类型": event.event_type,
            "用户ID(脱敏)": mask_identifier(event.user_id),
            "访客ID(脱敏)": mask_identifier(event.visitor_id),
            "会话ID(脱敏)": mask_identifier(event.session_id),
            "商品ID": event.product_id or "",
            "商品名称": self._metadata_value(event, "productName", "product_name"),
            "品牌": self._metadata_value(event, "brand"),
            "类目": self._metadata_value(event, "category"),
            "渠道": event.channel_id,
            "搜索关键词": event.search_keyword or "",
            "订单ID(脱敏)": mask_identifier(event.order_id),
            "支付ID(脱敏)": mask_identifier(event.payment_id),
            "成交金额": self._payment_amount(event),
            "发生时间": self._format_export_time(event.occurred_at),
        }

    def _user_profile_rows(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        profiles: dict[str, dict[str, object]] = {}
        for event in events:
            row = profiles.setdefault(
                event.subject_id,
                {
                    "userId": mask_identifier(event.subject_id),
                    "visits": 0,
                    "clicks": 0,
                    "favorites": 0,
                    "cartAdds": 0,
                    "orders": 0,
                    "payments": 0,
                    "salesAmount": 0.0,
                },
            )
            self._increment_profile(row, event)
        return list(profiles.values())

    def _user_segment_rows(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        rows = []
        for row in self._user_profile_rows(events):
            visits = int(row["visits"])
            carts = int(row["cartAdds"])
            payments = int(row["payments"])
            sales = float(row["salesAmount"])
            if payments > 0 and sales >= 1000:
                segment = "high_value"
            elif carts >= 2 and payments == 0:
                segment = "high_intent"
            elif visits == 0:
                segment = "silent"
            else:
                segment = "active"
            rows.append({**row, "segment": segment})
        return rows

    def _sales_conversion_rows(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        summary = BehaviorSummaryService().summarize(events)
        metrics = {str(metric["key"]): metric["value"] for metric in summary["metrics"]}  # type: ignore[index]
        return [
            {
                "visits": metrics.get("visits", 0),
                "orders": metrics.get("orders", 0),
                "payments": metrics.get("payments", 0),
                "salesAmount": metrics.get("sales_amount", 0),
                "averageOrderValue": metrics.get("average_order_value", 0),
                "paymentConversionRate": metrics.get("payment_conversion_rate", 0),
            }
        ]

    def _operation_effect_rows(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        summary = BehaviorSummaryService().summarize(events)
        metrics = [
            {"metric": metric["key"], "value": metric["value"], "unit": metric["unit"]}
            for metric in summary["metrics"]  # type: ignore[index]
        ]
        source_rows = [
            {"metric": f"source_{channel}", "value": count, "unit": "count"}
            for channel, count in summary["sourceDistribution"].items()  # type: ignore[union-attr]
        ]
        return metrics + source_rows

    def _increment_profile(self, row: dict[str, object], event: BehaviorEventRecord) -> None:
        field_by_event = {
            "browse": "visits",
            "click": "clicks",
            "favorite": "favorites",
            "cart_add": "cartAdds",
            "order_submit": "orders",
            "payment_success": "payments",
        }
        field = field_by_event.get(event.event_type)
        if field:
            row[field] = int(row[field]) + 1
        if event.event_type == "payment_success":
            row["salesAmount"] = round(float(row["salesAmount"]) + self._event_amount(event), 2)

    def _event_amount(self, event: BehaviorEventRecord) -> float:
        try:
            return max(float(event.metadata.get("amount", event.metadata.get("price", 0))), 0)
        except (TypeError, ValueError):
            return 0

    def _payment_amount(self, event: BehaviorEventRecord) -> str:
        if event.event_type != "payment_success":
            return ""
        return f"{self._event_amount(event):.2f}"

    def _metadata_value(self, event: BehaviorEventRecord, *keys: str) -> str:
        for key in keys:
            value = event.metadata.get(key)
            if value is not None:
                return str(value)
        return ""

    def _format_export_time(self, value: object) -> str:
        return value.isoformat() if hasattr(value, "isoformat") else str(value)

    def _csv_text(self, report_type: str, rows: list[dict[str, object]]) -> str:
        output = io.StringIO()
        fields = self._fields(report_type, rows)
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

    def _fields(self, report_type: str, rows: list[dict[str, object]]) -> list[str]:
        if rows:
            return list(rows[0].keys())
        defaults = {
            ReportType.BEHAVIOR_DETAIL.value: [
                "事件ID",
                "行为类型",
                "用户ID(脱敏)",
                "访客ID(脱敏)",
                "会话ID(脱敏)",
                "商品ID",
                "商品名称",
                "品牌",
                "类目",
                "渠道",
                "搜索关键词",
                "订单ID(脱敏)",
                "支付ID(脱敏)",
                "成交金额",
                "发生时间",
            ],
            ReportType.PRODUCT_ANALYSIS.value: ["productId", "productName", "rank", "value", "unit", "conversionRate"],
            ReportType.FUNNEL.value: ["stage", "enteredCount", "convertedCount", "dropoffCount", "conversionRate", "dropoffRate"],
            ReportType.SALES_CONVERSION.value: ["visits", "orders", "payments", "salesAmount", "averageOrderValue", "paymentConversionRate"],
            ReportType.OPERATION_EFFECT.value: ["metric", "value", "unit"],
        }
        return defaults.get(report_type, ["userId", "visits", "clicks", "cartAdds", "orders", "payments", "salesAmount"])

    def _write_file(self, principal: Principal, report_type: str, csv_text: str) -> str:
        self.storage_path.mkdir(parents=True, exist_ok=True)
        timestamp = utcnow().strftime("%Y%m%d%H%M%S")
        actor = self._safe_name(principal.actor_id)
        file_name = f"{report_type}-{actor}-{timestamp}.csv"
        (self.storage_path / file_name).write_text(csv_text, encoding="utf-8-sig")
        return file_name

    def _data_uri(self, csv_text: str) -> str:
        encoded = base64.b64encode(csv_text.encode("utf-8-sig")).decode("ascii")
        return f"data:text/csv;charset=utf-8;base64,{encoded}"

    def _normalize_report_type(self, report_type: str) -> str:
        known = {item.value for item in ReportType}
        if report_type in known:
            return report_type
        return ReportType.OPERATION_EFFECT.value

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("._") or "export"
