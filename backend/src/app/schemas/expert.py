"""Expert schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.app.models.expert import DegreeType, OrgType, QualificationStatus


# Base schemas
class ExpertBase(BaseModel):
    """Base expert schema."""

    degree_type: DegreeType | None = None
    degree_field: str | None = Field(None, max_length=100)
    career_years: int | None = Field(None, ge=0, le=50)
    position: str | None = Field(None, max_length=100)
    org_name: str | None = Field(None, max_length=200)
    org_type: OrgType | None = None
    specialties: list[str] | None = None
    certifications: list[dict] | None = None


class ExpertCreate(ExpertBase):
    """Expert creation schema."""

    user_id: UUID


class ExpertUpdate(ExpertBase):
    """Expert update schema."""

    pass


class ExpertInDB(ExpertBase):
    """Expert schema with database fields."""

    id: UUID
    user_id: UUID
    qualification_status: QualificationStatus
    qualification_note: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Expert(ExpertInDB):
    """Expert response schema."""

    pass


# Verification schemas
class QualificationCheck(BaseModel):
    """Qualification check result schema."""

    passed: bool
    reason: str


class QualificationVerifyRequest(ExpertBase):
    """Qualification verification request schema."""

    pass


class QualificationVerifyResponse(BaseModel):
    """Qualification verification response schema."""

    expert_id: UUID
    qualification_status: QualificationStatus
    verification_details: dict[str, QualificationCheck]
    verified_at: datetime
