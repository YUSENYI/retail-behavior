from __future__ import annotations

from dataclasses import asdict

from api.compat import APIRouter
from reports.export_service import ExportService
from reports.report_service import ReportService
from security.audit_query_service import list_audit_logs
from security.auth import DataScope, Principal, Role

router = APIRouter()
default_principal = Principal("demo", Role.ADMINISTRATOR, DataScope.ALL)


@router.get("/reports")
def list_reports(report_type: str = "behavior_detail") -> dict[str, object]:
    return {"items": [ReportService().generate(report_type, {})]}


@router.post("/reports/{report_type}/exports")
def create_report_export(report_type: str) -> dict[str, object]:
    return ExportService().create_export(default_principal, report_type, {})


@router.get("/audit-logs")
def audit_logs() -> dict[str, object]:
    return {"items": [asdict(record) for record in list_audit_logs(default_principal)]}
