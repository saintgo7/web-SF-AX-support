"""Answer model for storing applicant responses."""
import enum
import uuid
from sqlalchemy import Enum, ForeignKey, String, Integer, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class AnswerStatus(str, enum.Enum):
    """Answer status enum."""

    DRAFT = "DRAFT"  # Draft, not submitted yet
    SUBMITTED = "SUBMITTED"  # Submitted for evaluation
    GRADED = "GRADED"  # Grading completed
    REVIEWED = "REVIEWED"  # Final review completed


class Answer(Base, UUIDMixin, TimestampMixin):
    """Answer model for applicant responses with versioning support."""

    __tablename__ = "answers"

    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # Answer version for tracking edits
    response_data: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Actual response content
    # For objective questions: {"value": "selected_option_id"} or {"value": ["opt1", "opt2"]}
    # For subjective questions: {"text": "answer text"}
    # For file questions: {"file_url": "s3://...", "file_name": "document.pdf"}

    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # Auto-graded or manual score
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)  # Copy from question.max_score
    is_correct: Mapped[bool | None] = mapped_column(
        nullable=True
    )  # For objective questions, auto-graded result

    grader_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Manual grader (for subjective)
    grader_comment: Mapped[str | None] = mapped_column(Text, nullable=True)  # Grader feedback
    status: Mapped[AnswerStatus] = mapped_column(
        Enum(AnswerStatus), nullable=False, default=AnswerStatus.DRAFT
    )  # Overall status

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, expert_id={self.expert_id}, question_id={self.question_id}, version={self.version}, score={self.score})>"
