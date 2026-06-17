from __future__ import annotations

from dataclasses import asdict

from api.compat import APIRouter, HTTPException, Request
from api.schemas.reports import ReportExportRequest
from domain.enums import ReportType
from reports.export_service import ExportService
from reports.report_service import ReportService
from security.audit_query_service import list_audit_logs
from security.auth import DataScope, PermissionDenied, Principal, Role, principal_from_headers

router = APIRouter()
default_principal = Principal("demo", Role.ADMINISTRATOR, DataScope.ALL)


@router.get("/reports")
def list_reports(report_type: str | None = None) -> dict[str, object]:
    service = ReportService()
    reports = service.list_reports(report_type)
    if not reports:
        report_types = [report_type] if report_type else [item.value for item in ReportType]
        reports = [
            service.generate(item, {}, created_by=default_principal.actor_id)
            for item in report_types
            if item is not None
        ]
    return {"items": reports}


@router.post("/reports/{report_type}/exports")
def create_report_export(
    report_type: str,
    export_request: ReportExportRequest,
    request: Request,
) -> dict[str, object]:
    principal = principal_from_headers(dict(request.headers))
    try:
        return ExportService().create_export(
            principal,
            report_type,
            export_request.filters,
            export_request.reason,
        )
    except PermissionDenied as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/audit-logs")
def audit_logs() -> dict[str, object]:
    return {"items": [asdict(record) for record in list_audit_logs(default_principal)]}
