"""Question and Category models for evaluation system."""
import enum
import uuid
from sqlalchemy import Enum, ForeignKey, String, Integer, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class QuestionType(str, enum.Enum):
    """Question type enum."""

    SINGLE = "SINGLE"  # Single choice
    MULTIPLE = "MULTIPLE"  # Multiple choice
    SHORT = "SHORT"  # Short answer
    ESSAY = "ESSAY"  # Essay/Long answer
    FILE = "FILE"  # File attachment


class Difficulty(str, enum.Enum):
    """Difficulty level enum."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Specialty(str, enum.Enum):
    """Expert specialty enum."""

    ML = "ML"  # Machine Learning
    DL = "DL"  # Deep Learning
    CV = "CV"  # Computer Vision
    DATA_INTELLIGENCE = "DATA_INTELLIGENCE"  # Data Intelligence
    COMPUTING_PLATFORM = "COMPUTING_PLATFORM"  # Computing Platform
    GENERAL = "GENERAL"  # General


class QuestionCategory(Base, UUIDMixin, TimestampMixin):
    """Question category model for organizing evaluation areas."""

    __tablename__ = "question_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Integer, nullable=False, default=10)  # Weight in percentage
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<QuestionCategory(id={self.id}, name={self.name}, weight={self.weight})>"


class Question(Base, UUIDMixin, TimestampMixin):
    """Question model for evaluation items."""

    __tablename__ = "questions"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("question_categories.id", ondelete="RESTRICT"), nullable=False
    )
    q_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # For SINGLE/MULTIPLE choice
    correct_answer: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Correct answer(s)
    scoring_rubric: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # For subjective scoring
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False, default=Difficulty.MEDIUM)
    target_specialties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # List of specialties
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)  # Answer explanation
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, type={self.q_type.value}, max_score={self.max_score})>"
