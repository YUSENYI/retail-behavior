from __future__ import annotations

from security.masking import mask_user


def test_unmasked_sensitive_data_is_not_returned_by_default() -> None:
    masked = mask_user({"phone": "13812345678", "email": "alice@example.com"})
    assert "12345678" not in masked["phone"]
    assert "alice" not in masked["email"]
