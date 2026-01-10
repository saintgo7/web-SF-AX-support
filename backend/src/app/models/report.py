"""Report model for generated reports and PDF exports."""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class ReportType(str, enum.Enum):
    """Types of reports that can be generated."""

    EXPERT_EVALUATION = "EXPERT_EVALUATION"  # Individual expert's evaluation report
    SYSTEM_SUMMARY = "SYSTEM_SUMMARY"  # Overall system statistics summary
    MATCHING_ANALYSIS = "MATCHING_ANALYSIS"  # Matching recommendation analysis
    CATEGORY_BREAKDOWN = "CATEGORY_BREAKDOWN"  # Performance by question category


class ReportStatus(str, enum.Enum):
    """Report generation status."""

    PENDING = "PENDING"  # Report generation queued
    PROCESSING = "PROCESSING"  # Currently generating
    COMPLETED = "COMPLETED"  # Successfully generated
    FAILED = "FAILED"  # Generation failed


class Report(Base, UUIDMixin, TimestampMixin):
    """Report model for storing generated reports.

    Reports are generated asynchronously and stored with their PDF file paths.
    This model tracks report parameters, status, and output data.
    """

    __tablename__ = "reports"

    # Report metadata
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Generation parameters (filter criteria used)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Report data (cached/computed data for the report)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # File storage
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size: Mapped[int | None] = mapped_column(nullable=True)

    # Status tracking
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING, index=True
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Who generated this report
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Target expert (for EXPERT_EVALUATION reports)
    expert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("experts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Processing timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Report(id={self.id}, type={self.report_type.value}, "
            f"status={self.status.value}, title='{self.title}')>"
        )
