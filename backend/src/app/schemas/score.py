"""Score schemas for grading and evaluation scoring."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryScoreSummary(BaseModel):
    """Score summary for a single category."""

    category_id: UUID
    category_name: str
    score: float = Field(ge=0)
    max_score: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    graded_count: int = Field(ge=0)
    total_count: int = Field(ge=0)


class ExpertScoreBase(BaseModel):
    """Base expert score schema."""

    total_score: float = Field(ge=0, default=0.0)
    max_possible_score: float = Field(ge=0, default=0.0)
    average_percentage: float = Field(ge=0, le=100, default=0.0)
    graded_count: int = Field(ge=0, default=0)
    total_count: int = Field(ge=0, default=0)


class ExpertScoreResponse(ExpertScoreBase):
    """Expert score response schema."""

    id: UUID
    expert_id: UUID
    category_scores: list[CategoryScoreSummary] = []
    rank: int | None = None
    percentile: float | None = None
    last_calculated_at: datetime

    model_config = {"from_attributes": True}


class ExpertScoreCreate(BaseModel):
    """Expert score create schema (internal use)."""

    expert_id: UUID


class GradingProgress(BaseModel):
    """Grading progress statistics."""

    total_answers: int = Field(ge=0)
    graded_answers: int = Field(ge=0)
    pending_answers: int = Field(ge=0)
    progress_percentage: float = Field(ge=0, le=100)

    # By status
    draft_count: int = Field(ge=0, default=0)
    submitted_count: int = Field(ge=0, default=0)
    graded_count: int = Field(ge=0, default=0)
    reviewed_count: int = Field(ge=0, default=0)


class GradingStatistics(BaseModel):
    """Overall grading statistics for admin/evaluator dashboard."""

    # Expert stats
    total_experts: int = Field(ge=0)
    experts_with_submissions: int = Field(ge=0)
    fully_graded_experts: int = Field(ge=0)

    # Answer stats
    total_answers: int = Field(ge=0)
    graded_answers: int = Field(ge=0)
    pending_answers: int = Field(ge=0)

    # Score distribution
    average_score: float = Field(ge=0)
    highest_score: float = Field(ge=0)
    lowest_score: float = Field(ge=0)

    # Today's activity
    graded_today: int = Field(ge=0)

    # Category breakdown
    category_stats: list[dict[str, Any]] = []


class AIGradeRequest(BaseModel):
    """Request for AI-assisted grading."""

    answer_id: UUID


class AIGradeResponse(BaseModel):
    """Response from AI-assisted grading."""

    answer_id: UUID
    question_id: UUID
    suggested_score: float = Field(ge=0)
    max_score: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1.0, description="AI confidence level (0-1)")
    reasoning: str = Field(description="AI reasoning for the score")
    matched_keywords: list[str] = Field(default=[], description="Keywords matched from rubric")
    rubric_coverage: float = Field(
        ge=0, le=100, description="Percentage of rubric criteria covered"
    )


class BatchGradeRequest(BaseModel):
    """Request for batch grading."""

    answer_ids: list[UUID] = Field(min_length=1, max_length=100)


class BatchGradeResponse(BaseModel):
    """Response from batch grading."""

    graded_count: int
    failed_count: int
    results: list[dict[str, Any]]  # List of grading results


class ScoreRecalculateRequest(BaseModel):
    """Request to recalculate expert scores."""

    expert_id: UUID


class ScoreRecalculateResponse(BaseModel):
    """Response from score recalculation."""

    expert_id: UUID
    previous_score: float
    new_score: float
    previous_percentage: float
    new_percentage: float
    recalculated_at: datetime
