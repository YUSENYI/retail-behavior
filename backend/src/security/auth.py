from __future__ import annotations

from dataclasses import dataclass, field

from domain.enums import DataScope, Role


class PermissionDenied(Exception):
    pass


@dataclass(slots=True)
class Principal:
    actor_id: str
    role: Role = Role.READ_ONLY_VIEWER
    data_scope: DataScope = DataScope.NONE
    scoped_ids: set[str] = field(default_factory=set)


ROLE_ACTIONS: dict[Role, set[str]] = {
    Role.ADMINISTRATOR: {"view", "create", "update", "handle", "export", "manage"},
    Role.OPERATIONS_MANAGER: {"view", "create", "update", "handle", "export"},
    Role.ANALYST: {"view", "export"},
    Role.CUSTOMER_SERVICE_VIEWER: {"view"},
    Role.READ_ONLY_VIEWER: {"view"},
}


def can(principal: Principal, resource: str, action: str, scope_id: str | None = None) -> bool:
    del resource
    if action not in ROLE_ACTIONS.get(principal.role, set()):
        return False
    if principal.data_scope == DataScope.ALL or principal.role == Role.ADMINISTRATOR:
        return True
    if principal.data_scope == DataScope.NONE:
        return action == "view" and principal.role == Role.READ_ONLY_VIEWER
    if scope_id is None:
        return True
    return scope_id in principal.scoped_ids


def assert_allowed(principal: Principal, resource: str, action: str, scope_id: str | None = None) -> None:
    if not can(principal, resource, action, scope_id):
        raise PermissionDenied(f"{principal.role} cannot {action} {resource}")


def principal_from_headers(headers: dict[str, str] | None = None) -> Principal:
    headers = headers or {}
    role = Role(headers.get("x-role", Role.ADMINISTRATOR.value))
    actor_id = headers.get("x-actor-id", "system")
    scope = DataScope(headers.get("x-data-scope", DataScope.ALL.value))
    scoped_ids = {value for value in headers.get("x-scoped-ids", "").split(",") if value}
    return Principal(actor_id=actor_id, role=role, data_scope=scope, scoped_ids=scoped_ids)
