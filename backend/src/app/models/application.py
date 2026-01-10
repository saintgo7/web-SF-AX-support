"""Application model for expert applications."""
import enum
import uuid
from sqlalchemy import Enum, ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class ApplicationStatus(str, enum.Enum):
    """Application status enum."""

    DRAFT = "DRAFT"  # 임시저장
    SUBMITTED = "SUBMITTED"  # 제출완료
    UNDER_REVIEW = "UNDER_REVIEW"  # 검토중
    APPROVED = "APPROVED"  # 승인
    REJECTED = "REJECTED"  # 반려
    WITHDRAWN = "WITHDRAWN"  # 철회


class ApplicationType(str, enum.Enum):
    """Application type enum."""

    NEW = "NEW"  # 신규 신청
    RENEWAL = "RENEWAL"  # 갱신 신청
    CHANGE = "CHANGE"  # 변경 신청


class Application(Base, UUIDMixin, TimestampMixin):
    """Application model for expert applications.

    Represents an application submitted by an expert for evaluation.
    Applications go through a review process before approval.
    """

    __tablename__ = "applications"

    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("experts.id", ondelete="CASCADE"),
        nullable=False,
    )
    application_type: Mapped[ApplicationType] = mapped_column(
        Enum(ApplicationType), nullable=False, default=ApplicationType.NEW
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.DRAFT
    )

    # Application content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Attached documents (list of file URLs/paths)
    documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Additional form data (flexible JSON structure)
    form_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Review information
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Version tracking for resubmissions
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, expert_id={self.expert_id}, status={self.status.value})>"
