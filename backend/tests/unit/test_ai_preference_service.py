from __future__ import annotations

from datetime import UTC, datetime

from services.ai_preference_service import AIUserPreferenceService, HashEmbeddingBackend
from services.behavior_event_repository import BehaviorEventRecord


def test_ai_preference_classifies_purchase_category_with_pretrained_backend_shape() -> None:
    events = [
        _event("e1", "user001", "browse", "SKU-001", "数码", "降噪蓝牙耳机", 399),
        _event("e2", "user001", "cart_add", "SKU-001", "数码", "降噪蓝牙耳机", 399),
        _event("e3", "user001", "payment_success", "SKU-001", "数码", "降噪蓝牙耳机", 399),
        _event("e4", "user001", "browse", "SKU-020", "食品", "低糖燕麦礼盒", 69),
        _event("e5", "user002", "payment_success", "SKU-020", "食品", "低糖燕麦礼盒", 69),
    ]

    result = AIUserPreferenceService(HashEmbeddingBackend()).classify(events)
    user001 = next(item for item in result["items"] if item["userId"] == "user001")

    assert result["behaviorWeights"]["payment_success"] > result["behaviorWeights"]["browse"]
    assert user001["primaryCategory"] == "数码"
    assert user001["primaryConfidence"] > 0
    assert user001["categories"][0]["evidenceProducts"][0]["productId"] == "SKU-001"


def _event(
    event_id: str,
    user_id: str,
    event_type: str,
    product_id: str,
    category: str,
    product_name: str,
    price: int,
) -> BehaviorEventRecord:
    return BehaviorEventRecord(
        event_id=event_id,
        source_system="test",
        event_type=event_type,
        user_id=user_id,
        visitor_id=f"visitor-{user_id}",
        session_id=f"session-{user_id}",
        product_id=product_id,
        channel_id="direct",
        occurred_at=datetime(2026, 6, 10, 10, 0, tzinfo=UTC),
        metadata={
            "category": category,
            "productName": product_name,
            "brand": "Demo",
            "price": price,
            "tag": "AI分类样本",
        },
    )
