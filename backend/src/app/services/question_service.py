"""Question service layer for business logic."""
from typing import Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.question import Question, QuestionCategory, QuestionType, Specialty
from src.app.schemas.question import QuestionCreate, QuestionUpdate, QuestionCategoryCreate, QuestionCategoryUpdate


class QuestionService:
    """Service for question and category management."""

    @staticmethod
    async def create_category(db: AsyncSession, category_data: QuestionCategoryCreate) -> QuestionCategory:
        """Create a new question category.

        Args:
            db: Database session
            category_data: Category creation data

        Returns:
            Created category
        """
        new_category = QuestionCategory(**category_data.model_dump())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category

    @staticmethod
    async def get_category(db: AsyncSession, category_id: Any) -> QuestionCategory | None:
        """Get category by ID.

        Args:
            db: Database session
            category_id: Category UUID

        Returns:
            Category or None
        """
        result = await db.execute(select(QuestionCategory).where(QuestionCategory.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_categories(
        db: AsyncSession, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> list[QuestionCategory]:
        """List all categories with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only return active categories

        Returns:
            List of categories
        """
        query = select(QuestionCategory).order_by(QuestionCategory.display_order, QuestionCategory.name)

        if active_only:
            query = query.where(QuestionCategory.is_active == True)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: Any, category_data: QuestionCategoryUpdate
    ) -> QuestionCategory | None:
        """Update a category.

        Args:
            db: Database session
            category_id: Category UUID
            category_data: Category update data

        Returns:
            Updated category or None
        """
        category = await QuestionService.get_category(db, category_id)
        if not category:
            return None

        for field, value in category_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: Any) -> bool:
        """Delete a category (soft delete by setting is_active=False).

        Args:
            db: Database session
            category_id: Category UUID

        Returns:
            True if deleted, False if not found
        """
        category = await QuestionService.get_category(db, category_id)
        if not category:
            return False

        category.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def create_question(db: AsyncSession, question_data: QuestionCreate) -> Question:
        """Create a new question.

        Args:
            db: Database session
            question_data: Question creation data

        Returns:
            Created question
        """
        # Verify category exists
        category = await QuestionService.get_category(db, question_data.category_id)
        if not category:
            raise ValueError(f"Category {question_data.category_id} not found")

        new_question = Question(**question_data.model_dump())
        db.add(new_question)
        await db.commit()
        await db.refresh(new_question)
        return new_question

    @staticmethod
    async def get_question(db: AsyncSession, question_id: Any) -> Question | None:
        """Get question by ID.

        Args:
            db: Database session
            question_id: Question UUID

        Returns:
            Question or None
        """
        result = await db.execute(select(Question).where(Question.id == question_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_questions(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Any = None,
        q_type: QuestionType = None,
        specialty: Specialty = None,
        active_only: bool = True,
    ) -> tuple[list[Question], int]:
        """List questions with filtering and pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_id: Filter by category
            q_type: Filter by question type
            specialty: Filter by target specialty
            active_only: Only return active questions

        Returns:
            Tuple of (list of questions, total count)
        """
        # Build base query
        count_query = select(func.count(Question.id))
        query = select(Question).order_by(Question.display_order, Question.created_at)

        filters = []
        if active_only:
            filters.append(Question.is_active == True)
        if category_id:
            filters.append(Question.category_id == category_id)
        if q_type:
            filters.append(Question.q_type == q_type)
        if specialty:
            # Filter by target_specialties JSONB array
            filters.append(Question.target_specialties.contains([specialty.value]))

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        questions = list(result.scalars().all())

        return questions, total

    @staticmethod
    async def update_question(
        db: AsyncSession, question_id: Any, question_data: QuestionUpdate
    ) -> Question | None:
        """Update a question.

        Args:
            db: Database session
            question_id: Question UUID
            question_data: Question update data

        Returns:
            Updated question or None
        """
        question = await QuestionService.get_question(db, question_id)
        if not question:
            return None

        # If updating category_id, verify it exists
        if question_data.category_id and question_data.category_id != question.category_id:
            category = await QuestionService.get_category(db, question_data.category_id)
            if not category:
                raise ValueError(f"Category {question_data.category_id} not found")

        for field, value in question_data.model_dump(exclude_unset=True).items():
            setattr(question, field, value)

        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def delete_question(db: AsyncSession, question_id: Any) -> bool:
        """Delete a question (soft delete by setting is_active=False).

        Args:
            db: Database session
            question_id: Question UUID

        Returns:
            True if deleted, False if not found
        """
        question = await QuestionService.get_question(db, question_id)
        if not question:
            return False

        question.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def get_questions_by_specialties(
        db: AsyncSession, specialties: list[Specialty], active_only: bool = True
    ) -> list[Question]:
        """Get questions filtered by expert specialties.

        Args:
            db: Database session
            specialties: List of expert specialties
            active_only: Only return active questions

        Returns:
            List of matching questions
        """
        if not specialties:
            return []

        # Filter questions that match ANY of the specialties or have no target restriction
        query = select(Question)

        filters = []
        if active_only:
            filters.append(Question.is_active == True)

        # Build OR condition for specialties
        specialty_filters = [
            Question.target_specialties.contains([specialty.value]) for specialty in specialties
        ]
        # Also include questions with no specialty restriction
        specialty_filters.append(Question.target_specialties == None)

        if filters:
            filters.append(or_(*specialty_filters))
            query = query.where(and_(*filters))
        else:
            query = query.where(or_(*specialty_filters))

        query = query.order_by(Question.display_order, Question.created_at)
        result = await db.execute(query)
        return list(result.scalars().all())
