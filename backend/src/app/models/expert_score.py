"""ExpertScore model for aggregated scoring data."""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class ExpertScore(Base, UUIDMixin, TimestampMixin):
    """ExpertScore model for storing aggregated expert evaluation scores.

    This model caches calculated scores to avoid expensive queries.
    Scores are recalculated after grading events.
    """

    __tablename__ = "expert_scores"

    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )

    # Aggregate scores
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_possible_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    average_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0-100

    # Category breakdown: {category_id: {score, max_score, percentage, graded_count}}
    category_scores: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Grading progress
    graded_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Rank among all experts (calculated periodically)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentile: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100

    # Last calculation timestamp
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<ExpertScore(id={self.id}, expert_id={self.expert_id}, "
            f"total_score={self.total_score}, average_percentage={self.average_percentage:.1f}%)>"
        )
