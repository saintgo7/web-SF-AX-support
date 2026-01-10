"""Application schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.app.models.application import ApplicationStatus, ApplicationType


# Base schemas
class ApplicationBase(BaseModel):
    """Base application schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    application_type: ApplicationType = ApplicationType.NEW
    documents: list[dict] | None = None
    form_data: dict | None = None


class ApplicationCreate(ApplicationBase):
    """Application creation schema."""

    expert_id: UUID


class ApplicationUpdate(BaseModel):
    """Application update schema."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    documents: list[dict] | None = None
    form_data: dict | None = None


class ApplicationSubmit(BaseModel):
    """Application submission schema."""

    pass  # No additional fields needed, just triggers status change


class ApplicationReview(BaseModel):
    """Application review schema (for admin/operator)."""

    status: ApplicationStatus = Field(..., description="New status: APPROVED or REJECTED")
    review_note: str | None = Field(None, description="Review notes/feedback")


class ApplicationInDB(ApplicationBase):
    """Application schema with database fields."""

    id: UUID
    expert_id: UUID
    status: ApplicationStatus
    reviewer_id: UUID | None = None
    review_note: str | None = None
    reviewed_at: str | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Application(ApplicationInDB):
    """Application response schema."""

    pass


class ApplicationList(BaseModel):
    """Application list response schema."""

    items: list[Application]
    total: int
    page: int
    page_size: int


class ApplicationSummary(BaseModel):
    """Application summary statistics schema."""

    total: int = 0
    draft: int = 0
    submitted: int = 0
    under_review: int = 0
    approved: int = 0
    rejected: int = 0
