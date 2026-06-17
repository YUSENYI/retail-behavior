from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Metric(BaseModel):
    key: str
    name: str
    value: float
    unit: str
    metricVersion: str
    freshnessAt: datetime | None = None
    validationState: str = "valid"


class FunnelStage(BaseModel):
    stage: str
    enteredCount: int = Field(ge=0)
    convertedCount: int = Field(ge=0)
    dropoffCount: int = Field(ge=0)
    conversionRate: float = Field(ge=0, le=100)
    dropoffRate: float = Field(ge=0, le=100)


class ProductHeat(BaseModel):
    productId: str
    productName: str
    rank: int = Field(ge=1)
    value: float = Field(ge=0)
    unit: str
    conversionRate: float = Field(ge=0, le=100)
