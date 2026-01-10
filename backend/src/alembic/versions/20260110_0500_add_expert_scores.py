"""Add expert_scores table for aggregated scoring.

Revision ID: a1b2c3d4e5f6
Revises: db81ce5e3704
Create Date: 2026-01-10 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "db81ce5e3704"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create expert_scores table for caching aggregated expert evaluation scores."""
    op.create_table(
        "expert_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "expert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("experts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Aggregate scores
        sa.Column("total_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("max_possible_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("average_percentage", sa.Float(), nullable=False, server_default="0.0"),
        # Category breakdown: {category_id: {score, max_score, percentage, graded_count}}
        sa.Column("category_scores", postgresql.JSONB(), nullable=False, server_default="{}"),
        # Grading progress
        sa.Column("graded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_count", sa.Integer(), nullable=False, server_default="0"),
        # Rank among all experts
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("percentile", sa.Float(), nullable=True),
        # Last calculation timestamp
        sa.Column(
            "last_calculated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        # Timestamp columns (from TimestampMixin)
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

    # Create indexes for efficient querying
    op.create_index(
        "ix_expert_scores_expert_id",
        "expert_scores",
        ["expert_id"],
        unique=True,
    )
    op.create_index(
        "ix_expert_scores_average_percentage",
        "expert_scores",
        ["average_percentage"],
    )
    op.create_index(
        "ix_expert_scores_rank",
        "expert_scores",
        ["rank"],
    )
    op.create_index(
        "ix_expert_scores_last_calculated_at",
        "expert_scores",
        ["last_calculated_at"],
    )


def downgrade() -> None:
    """Drop expert_scores table."""
    op.drop_index("ix_expert_scores_last_calculated_at", table_name="expert_scores")
    op.drop_index("ix_expert_scores_rank", table_name="expert_scores")
    op.drop_index("ix_expert_scores_average_percentage", table_name="expert_scores")
    op.drop_index("ix_expert_scores_expert_id", table_name="expert_scores")
    op.drop_table("expert_scores")
