from __future__ import annotations

from api.compat import APIRouter
from models.alerts_recommendations import Alert, RecommendationInsight
from models.behavior_event import BehaviorEvent
from models.database import SessionLocal, use_mysql_persistence
from models.foundation import Channel, Order, Payment, Product, Session as RetailSession, User, Visitor
from models.metrics import FunnelStageSnapshot, MetricSnapshot
from models.profiles import PurchaseIntent, UserProfile, UserSegment, UserSegmentMembership
from models.reports import Report
from security.audit import audit_recorder
from security.auth import DataScope, Principal, Role, assert_allowed
from services.behavior_event_repository import repository
from sqlalchemy import delete

router = APIRouter()
default_principal = Principal("admin001", Role.ADMINISTRATOR, DataScope.ALL)


@router.post("/system/reset")
def reset_system_data() -> dict[str, object]:
    assert_allowed(default_principal, "system", "manage")
    if use_mysql_persistence():
        with SessionLocal() as session:
            for model in [
                Report,
                RecommendationInsight,
                Alert,
                PurchaseIntent,
                UserSegmentMembership,
                UserSegment,
                UserProfile,
                FunnelStageSnapshot,
                MetricSnapshot,
                BehaviorEvent,
                Payment,
                Order,
                RetailSession,
                Visitor,
                User,
                Channel,
                Product,
            ]:
                session.execute(delete(model))
            session.commit()
    else:
        repository.clear()
    audit_recorder.clear()
    audit_recorder.log(default_principal, "reset", "system", result="success")
    return {
        "status": "reset",
        "cleared": [
            "behavior_events",
            "audit_logs",
            "metric_snapshots",
            "funnel_stage_snapshots",
            "users",
            "visitors",
            "channels",
            "sessions",
            "products",
            "orders",
            "payments",
            "profiles",
            "segments",
            "alerts",
            "recommendations",
            "reports",
        ],
    }
