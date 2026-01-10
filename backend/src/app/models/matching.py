"""Matching model for expert-company matching."""
import enum
import uuid
from sqlalchemy import Enum, ForeignKey, String, Text, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class MatchingStatus(str, enum.Enum):
    """Matching status enum."""

    PROPOSED = "PROPOSED"  # 제안됨
    ACCEPTED = "ACCEPTED"  # 수락됨
    REJECTED = "REJECTED"  # 거절됨
    IN_PROGRESS = "IN_PROGRESS"  # 진행중
    COMPLETED = "COMPLETED"  # 완료
    CANCELLED = "CANCELLED"  # 취소됨


class MatchingType(str, enum.Enum):
    """Matching type enum."""

    AUTO = "AUTO"  # 자동 매칭
    MANUAL = "MANUAL"  # 수동 매칭
    REQUESTED = "REQUESTED"  # 요청 매칭


class Matching(Base, UUIDMixin, TimestampMixin):
    """Matching model for expert-company matching.

    Represents a match between an expert and a company demand.
    """

    __tablename__ = "matchings"

    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("experts.id", ondelete="CASCADE"),
        nullable=False,
    )
    demand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("demands.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Matching details
    matching_type: Mapped[MatchingType] = mapped_column(
        Enum(MatchingType), nullable=False, default=MatchingType.AUTO
    )
    status: Mapped[MatchingStatus] = mapped_column(
        Enum(MatchingStatus), nullable=False, default=MatchingStatus.PROPOSED
    )

    # Matching score (0-100)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Score breakdown (detailed scoring factors)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Matching reason/notes
    matching_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Expert response
    expert_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    expert_responded_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Company feedback
    company_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5 stars

    # Matched by (admin user who created manual match)
    matched_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Project tracking
    project_start_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    project_end_date: Mapped[str | None] = mapped_column(String(50), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Matching(id={self.id}, expert_id={self.expert_id}, demand_id={self.demand_id}, status={self.status.value})>"
