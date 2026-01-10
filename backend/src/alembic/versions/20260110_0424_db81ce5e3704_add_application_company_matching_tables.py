"""add_application_company_matching_tables

Revision ID: db81ce5e3704
Revises:
Create Date: 2026-01-10 04:24:33.662683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db81ce5e3704'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database - Add new tables for Application, Company, Demand, and Matching."""

    # Create companies table
    op.create_table('companies',
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('business_number', sa.String(length=20), nullable=True),
        sa.Column('industry', sa.String(length=50), nullable=False, server_default='MANUFACTURING'),
        sa.Column('size', sa.String(length=50), nullable=False, server_default='SMALL'),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('contact_name', sa.String(length=100), nullable=True),
        sa.Column('contact_email', sa.String(length=200), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('registered_by', sa.UUID(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['registered_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_number')
    )

    # Create applications table
    op.create_table('applications',
        sa.Column('expert_id', sa.UUID(), nullable=False),
        sa.Column('application_type', sa.String(length=50), nullable=False, server_default='NEW'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('documents', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('form_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reviewer_id', sa.UUID(), nullable=True),
        sa.Column('review_note', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.String(length=50), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['expert_id'], ['experts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create demands table
    op.create_table('demands',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_specialties', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expert_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('project_duration', sa.String(length=100), nullable=True),
        sa.Column('budget_range', sa.String(length=100), nullable=True),
        sa.Column('requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create matchings table
    op.create_table('matchings',
        sa.Column('expert_id', sa.UUID(), nullable=False),
        sa.Column('demand_id', sa.UUID(), nullable=False),
        sa.Column('matching_type', sa.String(length=50), nullable=False, server_default='AUTO'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PROPOSED'),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('score_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('matching_reason', sa.Text(), nullable=True),
        sa.Column('expert_response', sa.Text(), nullable=True),
        sa.Column('expert_responded_at', sa.String(length=50), nullable=True),
        sa.Column('company_feedback', sa.Text(), nullable=True),
        sa.Column('company_rating', sa.Integer(), nullable=True),
        sa.Column('matched_by', sa.UUID(), nullable=True),
        sa.Column('project_start_date', sa.String(length=50), nullable=True),
        sa.Column('project_end_date', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['demand_id'], ['demands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['experts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['matched_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better query performance
    op.create_index('idx_applications_expert_id', 'applications', ['expert_id'])
    op.create_index('idx_applications_status', 'applications', ['status'])
    op.create_index('idx_demands_company_id', 'demands', ['company_id'])
    op.create_index('idx_demands_status', 'demands', ['status'])
    op.create_index('idx_matchings_expert_id', 'matchings', ['expert_id'])
    op.create_index('idx_matchings_demand_id', 'matchings', ['demand_id'])
    op.create_index('idx_matchings_status', 'matchings', ['status'])


def downgrade() -> None:
    """Downgrade database - Remove Application, Company, Demand, and Matching tables."""

    # Drop indexes
    op.drop_index('idx_matchings_status', table_name='matchings')
    op.drop_index('idx_matchings_demand_id', table_name='matchings')
    op.drop_index('idx_matchings_expert_id', table_name='matchings')
    op.drop_index('idx_demands_status', table_name='demands')
    op.drop_index('idx_demands_company_id', table_name='demands')
    op.drop_index('idx_applications_status', table_name='applications')
    op.drop_index('idx_applications_expert_id', table_name='applications')

    # Drop tables (in reverse order of creation due to foreign keys)
    op.drop_table('matchings')
    op.drop_table('demands')
    op.drop_table('applications')
    op.drop_table('companies')
