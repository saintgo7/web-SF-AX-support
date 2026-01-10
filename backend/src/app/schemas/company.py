"""Company and Demand schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from src.app.models.company import CompanySize, IndustryType, DemandStatus


# Company schemas
class CompanyBase(BaseModel):
    """Base company schema."""

    name: str = Field(..., min_length=1, max_length=200)
    business_number: str | None = Field(None, max_length=20)
    industry: IndustryType = IndustryType.MANUFACTURING
    size: CompanySize = CompanySize.SMALL
    employee_count: int | None = Field(None, ge=1)
    address: str | None = Field(None, max_length=500)
    contact_name: str | None = Field(None, max_length=100)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    description: str | None = None
    website: str | None = Field(None, max_length=500)


class CompanyCreate(CompanyBase):
    """Company creation schema."""

    pass


class CompanyUpdate(BaseModel):
    """Company update schema."""

    name: str | None = Field(None, min_length=1, max_length=200)
    business_number: str | None = Field(None, max_length=20)
    industry: IndustryType | None = None
    size: CompanySize | None = None
    employee_count: int | None = Field(None, ge=1)
    address: str | None = Field(None, max_length=500)
    contact_name: str | None = Field(None, max_length=100)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    description: str | None = None
    website: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class CompanyInDB(CompanyBase):
    """Company schema with database fields."""

    id: UUID
    registered_by: UUID | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Company(CompanyInDB):
    """Company response schema."""

    pass


class CompanyList(BaseModel):
    """Company list response schema."""

    items: list[Company]
    total: int
    page: int
    page_size: int


# Demand schemas
class DemandBase(BaseModel):
    """Base demand schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    required_specialties: list[str] | None = None
    expert_count: int = Field(1, ge=1, le=10)
    project_duration: str | None = Field(None, max_length=100)
    budget_range: str | None = Field(None, max_length=100)
    requirements: dict | None = None
    priority: int = Field(3, ge=1, le=5)


class DemandCreate(DemandBase):
    """Demand creation schema."""

    company_id: UUID


class DemandUpdate(BaseModel):
    """Demand update schema."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    required_specialties: list[str] | None = None
    expert_count: int | None = Field(None, ge=1, le=10)
    project_duration: str | None = Field(None, max_length=100)
    budget_range: str | None = Field(None, max_length=100)
    requirements: dict | None = None
    priority: int | None = Field(None, ge=1, le=5)
    status: DemandStatus | None = None
    is_active: bool | None = None


class DemandInDB(DemandBase):
    """Demand schema with database fields."""

    id: UUID
    company_id: UUID
    status: DemandStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Demand(DemandInDB):
    """Demand response schema."""

    pass


class DemandWithCompany(Demand):
    """Demand with company info response schema."""

    company: Company


class DemandList(BaseModel):
    """Demand list response schema."""

    items: list[Demand]
    total: int
    page: int
    page_size: int


class DemandSummary(BaseModel):
    """Demand summary statistics schema."""

    total: int = 0
    pending: int = 0
    matched: int = 0
    in_progress: int = 0
    completed: int = 0
