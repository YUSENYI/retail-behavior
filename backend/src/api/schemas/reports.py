from __future__ import annotations

from pydantic import BaseModel


class ReportExportRequest(BaseModel):
    filters: dict[str, object]
    reason: str | None = None


class ReportResponse(BaseModel):
    reportId: str
    reportType: str
    filters: dict[str, object]
    status: str
    sensitiveDataState: str
    exportUri: str | None = None
    freshnessAt: str | None = None


class AuditLogResponse(BaseModel):
    auditId: str
    actorId: str
    action: str
    resourceType: str
    result: str
    createdAt: str
