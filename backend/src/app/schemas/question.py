"""Question and Category schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.app.models.question import QuestionType, Difficulty, Specialty


# Category Schemas
class QuestionCategoryBase(BaseModel):
    """Base question category schema."""

    name: str = Field(..., max_length=100)
    description: str | None = None
    weight: int = Field(..., ge=0, le=100)
    display_order: int = Field(0, ge=0)
    is_active: bool = True


class QuestionCategoryCreate(QuestionCategoryBase):
    """Question category creation schema."""

    pass


class QuestionCategoryUpdate(QuestionCategoryBase):
    """Question category update schema."""

    pass


class QuestionCategoryInDB(QuestionCategoryBase):
    """Question category schema with database fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class QuestionCategory(QuestionCategoryInDB):
    """Question category response schema."""

    pass


# Question Schemas
class QuestionBase(BaseModel):
    """Base question schema."""

    category_id: UUID
    q_type: QuestionType
    content: str = Field(..., min_length=1)
    options: dict | None = None  # For SINGLE/MULTIPLE: {"A": "Option A", "B": "Option B", ...}
    correct_answer: dict | None = None  # For SINGLE: {"value": "A"}, MULTIPLE: {"value": ["A", "B"]}
    scoring_rubric: dict | None = None  # For subjective: {"excellent": "...", "good": "...", ...}
    max_score: int = Field(..., gt=0)
    difficulty: Difficulty = Difficulty.MEDIUM
    target_specialties: list[Specialty] | None = None  # Target specialties for this question
    explanation: str | None = None
    display_order: int = Field(0, ge=0)
    is_active: bool = True


class QuestionCreate(QuestionBase):
    """Question creation schema."""

    pass


class QuestionUpdate(QuestionBase):
    """Question update schema."""

    pass


class QuestionInDB(QuestionBase):
    """Question schema with database fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Question(QuestionInDB):
    """Question response schema."""

    pass


# Query schemas
class QuestionQuery(BaseModel):
    """Question query schema for filtering."""

    category_id: UUID | None = None
    q_type: QuestionType | None = None
    difficulty: Difficulty | None = None
    specialty: Specialty | None = None  # Filter by target specialty
    is_active: bool | None = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)


class QuestionListResponse(BaseModel):
    """Paginated question list response."""

    items: list[Question]
    total: int
    skip: int
    limit: int
