from __future__ import annotations

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    alertId: str
    alertType: str
    severity: str
    status: str
    triggerReason: str


class AlertUpdateRequest(BaseModel):
    status: str
    reason: str | None = None


class RecommendationInsightResponse(BaseModel):
    insightId: str
    targetType: str
    targetId: str
    productId: str
    basisType: str
    reason: str
    priority: str
    score: float = Field(ge=0, le=100)
