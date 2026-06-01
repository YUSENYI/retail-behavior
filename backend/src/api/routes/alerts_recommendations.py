from __future__ import annotations

from api.compat import APIRouter
from jobs.alert_recommendation_job import refresh_alerts_and_recommendations
from security.auth import DataScope, Principal, Role
from services.alert_workflow_service import AlertWorkflowService

router = APIRouter()
default_principal = Principal("demo", Role.ADMINISTRATOR, DataScope.ALL)


@router.get("/alerts")
def list_alerts() -> dict[str, object]:
    return {"items": refresh_alerts_and_recommendations()["alerts"]}


@router.patch("/alerts/{alert_id}")
def update_alert_status(alert_id: str, status: str = "acknowledged") -> dict[str, object]:
    new_status = AlertWorkflowService().transition(default_principal, "new", status, alert_id)
    return {"alertId": alert_id, "status": new_status}


@router.get("/recommendations/analysis")
def list_recommendation_insights(target_id: str = "demo-user") -> dict[str, object]:
    return {"items": refresh_alerts_and_recommendations(target_id)["recommendations"]}
