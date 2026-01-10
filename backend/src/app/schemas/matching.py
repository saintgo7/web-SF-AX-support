"""Matching schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.app.models.matching import MatchingStatus, MatchingType


# Base schemas
class MatchingBase(BaseModel):
    """Base matching schema."""

    matching_type: MatchingType = MatchingType.AUTO
    matching_reason: str | None = None


class MatchingCreate(MatchingBase):
    """Matching creation schema (for manual matching)."""

    expert_id: UUID
    demand_id: UUID
    match_score: float | None = Field(None, ge=0, le=100)


class MatchingUpdate(BaseModel):
    """Matching update schema."""

    status: MatchingStatus | None = None
    matching_reason: str | None = None
    expert_response: str | None = None
    company_feedback: str | None = None
    company_rating: int | None = Field(None, ge=1, le=5)
    project_start_date: str | None = None
    project_end_date: str | None = None


class MatchingExpertResponse(BaseModel):
    """Expert response to matching proposal."""

    accept: bool
    response_message: str | None = None


class MatchingCompanyFeedback(BaseModel):
    """Company feedback for completed matching."""

    rating: int = Field(..., ge=1, le=5)
    feedback: str | None = None


class MatchingInDB(MatchingBase):
    """Matching schema with database fields."""

    id: UUID
    expert_id: UUID
    demand_id: UUID
    status: MatchingStatus
    match_score: float | None = None
    score_breakdown: dict | None = None
    expert_response: str | None = None
    expert_responded_at: str | None = None
    company_feedback: str | None = None
    company_rating: int | None = None
    matched_by: UUID | None = None
    project_start_date: str | None = None
    project_end_date: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Matching(MatchingInDB):
    """Matching response schema."""

    pass


class MatchingWithDetails(Matching):
    """Matching with expert and demand details."""

    expert_name: str | None = None
    expert_specialties: list[str] | None = None
    demand_title: str | None = None
    company_name: str | None = None


class MatchingList(BaseModel):
    """Matching list response schema."""

    items: list[Matching]
    total: int
    page: int
    page_size: int


class MatchingSummary(BaseModel):
    """Matching summary statistics schema."""

    total: int = 0
    proposed: int = 0
    accepted: int = 0
    rejected: int = 0
    in_progress: int = 0
    completed: int = 0


# Auto-matching schemas
class AutoMatchRequest(BaseModel):
    """Auto-matching request schema."""

    demand_id: UUID
    max_candidates: int = Field(5, ge=1, le=20)
    min_score: float = Field(60.0, ge=0, le=100)


class MatchCandidate(BaseModel):
    """Match candidate schema."""

    expert_id: UUID
    expert_name: str
    match_score: float
    score_breakdown: dict
    specialties: list[str] | None = None
    qualification_status: str


class AutoMatchResponse(BaseModel):
    """Auto-matching response schema."""

    demand_id: UUID
    candidates: list[MatchCandidate]
    total_candidates: int


# Enhanced matching schemas (Sprint 6)
class MatchScoreBreakdown(BaseModel):
    """Detailed score breakdown for intelligent matching."""

    specialty: float = Field(..., description="전문분야 일치 점수 (40%)")
    qualification: float = Field(..., description="자격 검증 점수 (15%)")
    career: float = Field(..., description="경력 점수 (15%)")
    evaluation: float = Field(..., description="평가 점수 (20%)")
    availability: float = Field(..., description="가용성 점수 (10%)")


class RecommendedCandidate(BaseModel):
    """Recommended candidate with intelligent scoring."""

    expert_id: UUID
    expert_name: str
    total_score: float = Field(..., ge=0, le=100)
    score_breakdown: MatchScoreBreakdown
    recommendation_reasons: list[str]
    specialties: list[str] | None = None
    qualification_status: str


class RecommendRequest(BaseModel):
    """Request for intelligent recommendations."""

    demand_id: UUID
    top_n: int = Field(10, ge=1, le=50, description="최대 추천 수")
    min_score: float = Field(50.0, ge=0, le=100, description="최소 점수 임계값")


class RecommendResponse(BaseModel):
    """Response with intelligent recommendations."""

    demand_id: UUID
    demand_title: str | None = None
    candidates: list[RecommendedCandidate]
    total_candidates: int
    algorithm_version: str = "v1.0"


class CompatibilityCheckResponse(BaseModel):
    """Compatibility check between expert and demand."""

    expert_id: str
    demand_id: str
    total_score: float
    score_breakdown: MatchScoreBreakdown
    recommendation: str  # HIGHLY_RECOMMENDED, RECOMMENDED, POSSIBLE, NOT_RECOMMENDED
    recommendation_text: str  # Korean text
    reasons: list[str]
    details: dict


class MatchingAnalytics(BaseModel):
    """Matching analytics and statistics."""

    status_distribution: dict[str, int]
    success_rate: float
    average_match_score: float
    total_active_matchings: int
    total_completed: int
    top_matched_experts: list[dict]
