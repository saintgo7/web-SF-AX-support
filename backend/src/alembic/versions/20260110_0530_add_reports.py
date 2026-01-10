"""Add reports table for PDF generation.

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-10 05:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create reports table for storing generated reports."""
    # Create report type enum
    report_type_enum = postgresql.ENUM(
        "EXPERT_EVALUATION", "SYSTEM_SUMMARY", "MATCHING_ANALYSIS", "CATEGORY_BREAKDOWN",
        name="reporttype",
        create_type=True,
    )
    report_type_enum.create(op.get_bind())

    # Create report status enum
    report_status_enum = postgresql.ENUM(
        "PENDING", "PROCESSING", "COMPLETED", "FAILED",
        name="reportstatus",
        create_type=True,
    )
    report_status_enum.create(op.get_bind())

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        # Report metadata
        sa.Column("report_type", report_type_enum, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        # Generation parameters and data
        sa.Column("parameters", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("data", postgresql.JSONB(), nullable=False, server_default="{}"),
        # File storage
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        # Status tracking
        sa.Column("status", report_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("error_message", sa.String(1000), nullable=True),
        # Who generated this report
        sa.Column(
            "generated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Target expert (for EXPERT_EVALUATION reports)
        sa.Column(
            "expert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("experts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Processing timestamps
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamp columns
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_reports_report_type", "reports", ["report_type"])
    op.create_index("ix_reports_status", "reports", ["status"])
    op.create_index("ix_reports_generated_by", "reports", ["generated_by"])
    op.create_index("ix_reports_expert_id", "reports", ["expert_id"])
    op.create_index("ix_reports_created_at", "reports", ["created_at"])


def downgrade() -> None:
    """Drop reports table."""
    op.drop_index("ix_reports_created_at", table_name="reports")
    op.drop_index("ix_reports_expert_id", table_name="reports")
    op.drop_index("ix_reports_generated_by", table_name="reports")
    op.drop_index("ix_reports_status", table_name="reports")
    op.drop_index("ix_reports_report_type", table_name="reports")
    op.drop_table("reports")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS reportstatus")
    op.execute("DROP TYPE IF EXISTS reporttype")
