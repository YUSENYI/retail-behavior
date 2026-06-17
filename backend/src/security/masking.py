from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def mask_phone(value: str | None) -> str | None:
    if not value:
        return value
    if len(value) < 7:
        return "*" * len(value)
    return f"{value[:3]}****{value[-4:]}"


def mask_email(value: str | None) -> str | None:
    if not value or "@" not in value:
        return value
    name, domain = value.split("@", 1)
    visible = name[:1] or "*"
    return f"{visible}***@{domain}"


def mask_address(value: str | None) -> str | None:
    if not value:
        return value
    return value[:6] + "***" if len(value) > 6 else "***"


def mask_identifier(value: str | None) -> str | None:
    if not value:
        return value
    if len(value) <= 6:
        return "*" * len(value)
    return f"{value[:2]}***{value[-4:]}"


def mask_user(data: Mapping[str, Any]) -> dict[str, Any]:
    masked = dict(data)
    if "phone" in masked:
        masked["phone"] = mask_phone(masked["phone"])
    if "email" in masked:
        masked["email"] = mask_email(masked["email"])
    if "address" in masked:
        masked["address"] = mask_address(masked["address"])
    return masked


def mask_payment(data: Mapping[str, Any]) -> dict[str, Any]:
    masked = dict(data)
    if "payment_identifier" in masked:
        masked["payment_identifier"] = mask_identifier(masked["payment_identifier"])
    return masked
