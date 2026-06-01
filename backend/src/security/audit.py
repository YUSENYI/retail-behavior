from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from domain.common import utcnow
from models.database import SessionLocal, use_mysql_persistence
from models.security import AuditLog
from security.auth import Principal
from sqlalchemy import delete, select


@dataclass(slots=True)
class AuditRecord:
    audit_id: str
    actor_id: str
    actor_role: str
    action: str
    resource_type: str
    resource_id: str | None
    result: str
    reason: str | None
    created_at: datetime


class AuditRecorder:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    @property
    def records(self) -> list[AuditRecord]:
        return list(self._records)

    def log(
        self,
        principal: Principal,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        result: str = "success",
        reason: str | None = None,
    ) -> AuditRecord:
        record = AuditRecord(
            audit_id=str(uuid4()),
            actor_id=principal.actor_id,
            actor_role=principal.role.value,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            reason=reason,
            created_at=utcnow(),
        )
        self._records.append(record)
        return record

    def clear(self) -> None:
        self._records.clear()


class MySQLAuditRecorder(AuditRecorder):
    @property
    def records(self) -> list[AuditRecord]:
        with SessionLocal() as session:
            rows = session.scalars(select(AuditLog).order_by(AuditLog.created_at)).all()
            return [self._to_record(row) for row in rows]

    def log(
        self,
        principal: Principal,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        result: str = "success",
        reason: str | None = None,
    ) -> AuditRecord:
        record = AuditRecord(
            audit_id=str(uuid4()),
            actor_id=principal.actor_id,
            actor_role=principal.role.value,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            reason=reason,
            created_at=utcnow(),
        )
        with SessionLocal() as session:
            session.add(
                AuditLog(
                    audit_id=record.audit_id,
                    actor_id=record.actor_id,
                    actor_role=record.actor_role,
                    action=record.action,
                    resource_type=record.resource_type,
                    resource_id=record.resource_id,
                    result=record.result,
                    reason=record.reason,
                    request_context=None,
                    created_at=record.created_at.replace(tzinfo=None),
                )
            )
            session.commit()
        return record

    def clear(self) -> None:
        with SessionLocal() as session:
            session.execute(delete(AuditLog))
            session.commit()

    @staticmethod
    def _to_record(row: AuditLog) -> AuditRecord:
        return AuditRecord(
            audit_id=row.audit_id,
            actor_id=row.actor_id,
            actor_role=row.actor_role,
            action=row.action,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            result=row.result,
            reason=row.reason,
            created_at=row.created_at,
        )


audit_recorder: AuditRecorder
if use_mysql_persistence():
    audit_recorder = MySQLAuditRecorder()
else:
    audit_recorder = AuditRecorder()
