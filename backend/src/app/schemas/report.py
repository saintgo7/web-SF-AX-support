"""Report schemas for PDF generation and reporting."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.app.models.report import ReportType, ReportStatus


class ReportBase(BaseModel):
    """Base report schema."""

    report_type: ReportType
    title: str = Field(max_length=255)
    parameters: dict[str, Any] = Field(default_factory=dict)


class ReportCreate(ReportBase):
    """Schema for creating a report."""

    expert_id: UUID | None = None


class ReportResponse(ReportBase):
    """Schema for report response."""

    id: UUID
    data: dict[str, Any] = Field(default_factory=dict)
    file_url: str | None = None
    file_size: int | None = None
    status: ReportStatus
    error_message: str | None = None
    generated_by: UUID | None = None
    expert_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Schema for paginated report list."""

    items: list[ReportResponse]
    total: int
    skip: int
    limit: int


# Expert Report Data Schemas
class ExpertReportScoreSummary(BaseModel):
    """Score summary for expert report."""

    total_score: float
    max_possible_score: float
    percentage: float
    rank: int | None = None
    percentile: float | None = None


class ExpertReportCategoryScore(BaseModel):
    """Category score for expert report."""

    category_id: str
    category_name: str
    score: float
    max_score: float
    percentage: float
    question_count: int
    answered_count: int


class ExpertReportAnswerDetail(BaseModel):
    """Answer detail for expert report."""

    question_id: str
    question_content: str
    question_type: str
    category_name: str
    response_summary: str
    score: float | None
    max_score: float
    grader_comment: str | None = None


class ExpertReportData(BaseModel):
    """Complete data structure for expert evaluation report."""

    expert_id: str
    expert_name: str
    email: str
    phone: str | None = None
    specialty: str | None = None
    organization: str | None = None

    # Score summary
    score_summary: ExpertReportScoreSummary

    # Category breakdown
    category_scores: list[ExpertReportCategoryScore]

    # Answer details (optional - can be long)
    answer_details: list[ExpertReportAnswerDetail] = []

    # Meta
    generated_at: datetime
    evaluation_period: str | None = None


# System Summary Report Data
class SystemReportCategorySummary(BaseModel):
    """Category summary for system report."""

    category_id: str
    category_name: str
    total_questions: int
    total_answers: int
    graded_answers: int
    average_score: float
    highest_score: float
    lowest_score: float


class SystemReportScoreDistribution(BaseModel):
    """Score distribution for system report."""

    range_start: float
    range_end: float
    count: int
    percentage: float


class SystemReportData(BaseModel):
    """Complete data structure for system summary report."""

    # Expert statistics
    total_experts: int
    experts_with_submissions: int
    fully_graded_experts: int
    average_expert_score: float

    # Answer statistics
    total_questions: int
    total_answers: int
    graded_answers: int
    pending_answers: int

    # Category breakdown
    category_summaries: list[SystemReportCategorySummary]

    # Score distribution (for histogram)
    score_distribution: list[SystemReportScoreDistribution]

    # Top performers
    top_performers: list[dict[str, Any]] = []

    # Meta
    generated_at: datetime
    report_period: str | None = None


# Report Generation Requests
class GenerateExpertReportRequest(BaseModel):
    """Request to generate an expert evaluation report."""

    expert_id: UUID
    include_answers: bool = Field(default=True, description="Include detailed answer breakdown")
    format: str = Field(default="pdf", description="Output format: pdf, json")


class GenerateSummaryReportRequest(BaseModel):
    """Request to generate a system summary report."""

    start_date: datetime | None = None
    end_date: datetime | None = None
    category_ids: list[UUID] | None = None
    format: str = Field(default="pdf", description="Output format: pdf, json")


class GenerateReportResponse(BaseModel):
    """Response from report generation request."""

    report_id: UUID
    status: ReportStatus
    message: str
    estimated_completion: datetime | None = None
