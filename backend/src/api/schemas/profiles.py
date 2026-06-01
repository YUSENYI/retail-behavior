from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    userId: str
    maskedUser: dict[str, object]
    consumptionLevel: str
    interestTags: list[str]
    activityLevel: str
    valueGrade: str
    updatedAt: str


class UserSegmentResponse(BaseModel):
    segmentId: str
    segmentType: str
    name: str
    memberCount: int = Field(ge=0)
    ruleDescription: str


class PurchaseIntentResponse(BaseModel):
    userId: str
    intentLevel: str
    basis: str
    score: float = Field(ge=0, le=100)
