from __future__ import annotations

from analytics.product_heat_service import ProductHeatService
from conftest import load_fixture
from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord, InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService


def test_product_heat_has_non_negative_counts() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    heat = ProductHeatService().rank(repo.accepted_events(), "browse")
    assert heat["items"][0]["value"] >= 0


def test_product_heat_purchase_rank_uses_real_payment_events() -> None:
    now = utcnow()
    events = [
        BehaviorEventRecord(
            event_id="evt-browse-sku-001",
            source_system="web",
            event_type="browse",
            user_id="user-001",
            session_id="session-001",
            product_id="SKU-001",
            channel_id="direct",
            occurred_at=now,
            metadata={"productName": "Real Sales Product"},
        ),
        BehaviorEventRecord(
            event_id="evt-pay-sku-001",
            source_system="web",
            event_type="payment_success",
            user_id="user-001",
            session_id="session-001",
            product_id="SKU-001",
            order_id="order-001",
            payment_id="payment-001",
            channel_id="direct",
            occurred_at=now,
            metadata={"productName": "Real Sales Product", "quantity": 2},
        ),
    ]

    heat = ProductHeatService().rank(events, "sales")

    assert heat["items"] == [
        {
            "productId": "SKU-001",
            "productName": "Real Sales Product",
            "rank": 1,
            "value": 2,
            "unit": "count",
            "conversionRate": 100,
        }
    ]
