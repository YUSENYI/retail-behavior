from __future__ import annotations

from security.masking import mask_address, mask_email, mask_identifier, mask_phone, mask_user


def test_masks_phone_email_address_and_payment_identifier() -> None:
    assert mask_phone("13812345678") == "138****5678"
    assert mask_email("alice@example.com") == "a***@example.com"
    assert mask_address("Shanghai Pudong") == "Shangh***"
    assert mask_identifier("pay_123456789") == "pa***6789"


def test_mask_user_defaults_sensitive_fields() -> None:
    masked = mask_user({"phone": "13812345678", "email": "alice@example.com", "address": "Shanghai Pudong"})
    assert masked["phone"] == "138****5678"
    assert masked["email"] == "a***@example.com"
    assert masked["address"] == "Shangh***"
