"""Answer schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.app.models.answer import AnswerStatus


class AnswerBase(BaseModel):
    """Base answer schema."""

    expert_id: UUID
    question_id: UUID
    response_data: dict = Field(..., description="Response content")


class AnswerCreate(AnswerBase):
    """Answer creation schema."""

    pass


class AnswerUpdate(BaseModel):
    """Answer update schema."""

    response_data: dict | None = None
    status: AnswerStatus | None = None


class AnswerInDB(AnswerBase):
    """Answer schema with database fields."""

    id: UUID
    version: int
    score: float | None = None
    max_score: int
    is_correct: bool | None = None
    grader_id: UUID | None = None
    grader_comment: str | None = None
    status: AnswerStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Answer(AnswerInDB):
    """Answer response schema."""

    pass


# Grading related schemas
class AutoGradeRequest(BaseModel):
    """Auto grade request schema."""

    answer_id: UUID


class AutoGradeResponse(BaseModel):
    """Auto grade response schema."""

    answer_id: UUID
    score: float
    max_score: int
    is_correct: bool | None = None
    feedback: str | None = None


class ManualGradeRequest(BaseModel):
    """Manual grade request schema for subjective questions."""

    score: float = Field(..., ge=0)
    grader_comment: str | None = None


class ManualGradeResponse(BaseModel):
    """Manual grade response schema."""

    answer_id: UUID
    score: float
    max_score: int
    grader_comment: str | None = None
    graded_at: datetime


class AnswerSubmitRequest(BaseModel):
    """Answer submit request schema for batch submission."""

    answers: list[AnswerCreate] = Field(..., min_length=1, max_length=50)


class AnswerSubmitResponse(BaseModel):
    """Answer submit response schema."""

    submitted_count: int
    answer_ids: list[UUID]
    message: str


class ExpertAnswersResponse(BaseModel):
    """Expert answers summary response."""

    expert_id: UUID
    total_questions: int
    answered_count: int
    total_score: float | None = None
    max_total_score: int
    answers: list[Answer]
