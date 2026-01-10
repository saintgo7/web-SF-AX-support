# Database Migration Guide - Sprint 3: AX Q&A System

## Overview

This guide explains how to create and apply database migrations for the new Question and Answer evaluation system models.

## New Models

### 1. Question Models (`src/app/models/question.py`)
- `QuestionCategory`: Organizes evaluation areas
- `Question`: Individual evaluation questions with multiple types
- Enums: `QuestionType`, `Difficulty`, `Specialty`

### 2. Answer Model (`src/app/models/answer.py`)
- `Answer`: Stores applicant responses with versioning
- Enum: `AnswerStatus`

## Prerequisites

Ensure you have:
1. PostgreSQL database running
2. Alembic configured in your project
3. Environment variables set (`DATABASE_URL`)

## Step 1: Generate Migration

Using Alembic CLI, generate a new migration:

```bash
cd backend

# Activate virtual environment if needed
source venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Generate migration
alembic revision --autogenerate -m "Add questions and answers tables for evaluation system"
```

This will create a new migration file in `src/alembic/versions/`.

## Step 2: Review Migration

Open the generated migration file and verify it includes:

### Expected Operations:

1. **Create `question_categories` table:**
   - id (UUID, PK)
   - name (VARCHAR, unique, not null)
   - description (TEXT)
   - weight (INTEGER, not null, default 10)
   - display_order (INTEGER, not null, default 0)
   - is_active (BOOLEAN, not null, default True)
   - created_at, updated_at (TIMESTAMP)

2. **Create `questions` table:**
   - id (UUID, PK)
   - category_id (UUID, FK to question_categories)
   - q_type (ENUM: SINGLE, MULTIPLE, SHORT, ESSAY, FILE)
   - content (TEXT, not null)
   - options (JSONB)
   - correct_answer (JSONB)
   - scoring_rubric (JSONB)
   - max_score (INTEGER, not null)
   - difficulty (ENUM: EASY, MEDIUM, HARD)
   - target_specialties (JSONB)
   - explanation (TEXT)
   - display_order (INTEGER, default 0)
   - is_active (BOOLEAN, default True)
   - created_at, updated_at (TIMESTAMP)

3. **Create `answers` table:**
   - id (UUID, PK)
   - expert_id (UUID, FK to experts, ondelete CASCADE)
   - question_id (UUID, FK to questions, ondelete CASCADE)
   - version (INTEGER, not null, default 1)
   - response_data (JSONB, not null)
   - score (FLOAT)
   - max_score (INTEGER, not null)
   - is_correct (BOOLEAN)
   - grader_id (UUID, FK to users, ondelete SET NULL)
   - grader_comment (TEXT)
   - status (ENUM: DRAFT, SUBMITTED, GRADED, REVIEWED)
   - created_at, updated_at (TIMESTAMP)

4. **Create indexes:**
   - questions_category_id index
   - questions_target_specialties index (for JSONB queries)
   - answers_expert_id index
   - answers_question_id index
   - answers_status index

5. **Create foreign keys:**
   - questions.category_id → question_categories.id (RESTRICT)
   - answers.expert_id → experts.id (CASCADE)
   - answers.question_id → questions.id (CASCADE)
   - answers.grader_id → users.id (SET NULL)

## Step 3: Edit Migration (if needed)

If the auto-generated migration needs adjustments, edit it manually.

Example of what the migration might look like:

```python
"""add questions and answers tables

Revision ID: 001_add_qa_system
Revises: (previous_revision)
Create Date: 2025-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_qa_system'
down_revision = '000_initial'  # Your previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Create question_type enum
    question_type_enum = postgresql.ENUM(
        'SINGLE', 'MULTIPLE', 'SHORT', 'ESSAY', 'FILE',
        name='questiontype',
        create_type=True
    )
    question_type_enum.create(op.get_bind())

    # Create difficulty enum
    difficulty_enum = postgresql.ENUM(
        'EASY', 'MEDIUM', 'HARD',
        name='difficulty',
        create_type=True
    )
    difficulty_enum.create(op.get_bind())

    # Create answer_status enum
    answer_status_enum = postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'GRADED', 'REVIEWED',
        name='answerstatus',
        create_type=True
    )
    answer_status_enum.create(op.get_bind())

    # Create question_categories table
    op.create_table(
        'question_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=False, default=10),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('question_categories.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('q_type', question_type_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSONB(), nullable=True),
        sa.Column('correct_answer', postgresql.JSONB(), nullable=True),
        sa.Column('scoring_rubric', postgresql.JSONB(), nullable=True),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('difficulty', difficulty_enum, nullable=False, default='MEDIUM'),
        sa.Column('target_specialties', postgresql.JSONB(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create answers table
    op.create_table(
        'answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('experts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('response_data', postgresql.JSONB(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('grader_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('grader_comment', sa.Text(), nullable=True),
        sa.Column('status', answer_status_enum, nullable=False, default='DRAFT'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create indexes
    op.create_index('ix_questions_category_id', 'questions', ['category_id'])
    op.create_index('ix_answers_expert_id', 'answers', ['expert_id'])
    op.create_index('ix_answers_question_id', 'answers', ['question_id'])
    op.create_index('ix_answers_status', 'answers', ['status'])

    # Create GIN index for JSONB queries
    op.create_index('ix_questions_target_specialties', 'questions', ['target_specialties'], postgresql_using='gin')


def downgrade():
    # Drop tables
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('question_categories')

    # Drop enums
    postgresql.ENUM(name='answerstatus').drop(op.get_bind())
    postgresql.ENUM(name='difficulty').drop(op.get_bind())
    postgresql.ENUM(name='questiontype').drop(op.get_bind())
```

## Step 4: Apply Migration

### Development Environment

```bash
# Apply migration to development database
alembic upgrade head

# Verify migration
alembic current
```

### Production Environment

**WARNING: Always backup your database before running migrations in production!**

```bash
# 1. Backup database
pg_dump -U username -h hostname -d database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Review migration plan
alembic history

# 3. Test migration in staging first!
# 4. Apply to production
alembic upgrade head
```

## Step 5: Verify Migration

Connect to your database and verify:

```sql
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('question_categories', 'questions', 'answers');

-- Check enums exist
SELECT typname
FROM pg_type
WHERE typname IN ('questiontype', 'difficulty', 'answerstatus');

-- Check sample data (optional)
SELECT COUNT(*) FROM question_categories;
SELECT COUNT(*) FROM questions;
SELECT COUNT(*) FROM answers;
```

## Step 6: Seed Initial Data (Optional)

Create a seed script to populate initial categories and questions:

```python
# src/alembic/seed_data.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.session import async_session_maker
from src.app.models.question import QuestionCategory, Question, QuestionType, Difficulty, Specialty


async def seed_questions():
    async with async_session_maker() as session:
        # Create categories
        ml_category = QuestionCategory(
            name="Machine Learning",
            description="ML algorithms and concepts",
            weight=20,
            display_order=1,
        )
        session.add(ml_category)

        dl_category = QuestionCategory(
            name="Deep Learning",
            description="Neural networks and deep learning",
            weight=20,
            display_order=2,
        )
        session.add(dl_category)

        await session.flush()

        # Create sample questions
        q1 = Question(
            category_id=ml_category.id,
            q_type=QuestionType.SINGLE,
            content="What is the purpose of cross-validation?",
            options={
                "A": "To increase training speed",
                "B": "To evaluate model generalization",
                "C": "To reduce memory usage",
                "D": "To improve accuracy",
            },
            correct_answer={"value": "B"},
            max_score=10,
            difficulty=Difficulty.EASY,
            target_specialties=[Specialty.ML],
            explanation="Cross-validation helps assess how well a model generalizes to unseen data.",
        )
        session.add(q1)

        await session.commit()
        print("Seed data created successfully!")


if __name__ == "__main__":
    asyncio.run(seed_questions())
```

Run seed script:
```bash
python -m src.alembic.seed_data
```

## Troubleshooting

### Migration fails with "relation already exists"
```bash
# Drop and recreate (development only!)
alembic downgrade base
alembic upgrade head
```

### Foreign key constraint errors
- Ensure `experts` and `users` tables exist
- Check that referenced IDs are valid

### JSONB issues
- Ensure PostgreSQL version supports JSONB (9.4+)
- Check that dialect is set to `postgresql`

## Rollback

If needed, rollback the migration:

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Complete rollback
alembic downgrade base
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

## Post-Migration Checklist

- [ ] Migration applied successfully
- [ ] All tables created with correct structure
- [ ] Indexes created for performance
- [ ] Foreign keys working correctly
- [ ] Enums accessible from application
- [ ] Sample data seeded (if applicable)
- [ ] API endpoints tested with new models
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation updated

---

**Last Updated:** 2025-01-10
**Sprint:** 3 - AX Q&A System
**Author:** Development Team
