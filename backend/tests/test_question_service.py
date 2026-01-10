"""Unit tests for Question Service."""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.question import Question, QuestionCategory, QuestionType, Difficulty, Specialty
from src.app.schemas.question import QuestionCreate, QuestionCategoryCreate, QuestionUpdate
from src.app.services.question_service import QuestionService


@pytest.mark.asyncio
async def test_create_category(db_session: AsyncSession):
    """Test creating a question category."""
    category_data = QuestionCategoryCreate(
        name="Machine Learning",
        description="ML related questions",
        weight=20,
        display_order=1,
        is_active=True,
    )

    category = await QuestionService.create_category(db_session, category_data)

    assert category.id is not None
    assert category.name == "Machine Learning"
    assert category.weight == 20
    assert category.is_active is True


@pytest.mark.asyncio
async def test_get_category(db_session: AsyncSession):
    """Test getting a category by ID."""
    # Create category
    category_data = QuestionCategoryCreate(
        name="Deep Learning",
        description="DL related questions",
        weight=15,
    )
    created_category = await QuestionService.create_category(db_session, category_data)

    # Get category
    retrieved_category = await QuestionService.get_category(db_session, created_category.id)

    assert retrieved_category is not None
    assert retrieved_category.id == created_category.id
    assert retrieved_category.name == "Deep Learning"


@pytest.mark.asyncio
async def test_list_categories(db_session: AsyncSession):
    """Test listing categories with pagination."""
    # Create multiple categories
    for i in range(3):
        category_data = QuestionCategoryCreate(
            name=f"Category {i}",
            weight=10 + i,
            display_order=i,
        )
        await QuestionService.create_category(db_session, category_data)

    # List categories
    categories = await QuestionService.list_categories(db_session, skip=0, limit=10)

    assert len(categories) >= 3


@pytest.mark.asyncio
async def test_update_category(db_session: AsyncSession):
    """Test updating a category."""
    # Create category
    category_data = QuestionCategoryCreate(name="Original Name", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    # Update category
    update_data = QuestionCategoryUpdate(name="Updated Name", weight=20)
    updated_category = await QuestionService.update_category(db_session, category.id, update_data)

    assert updated_category is not None
    assert updated_category.name == "Updated Name"
    assert updated_category.weight == 20


@pytest.mark.asyncio
async def test_delete_category(db_session: AsyncSession):
    """Test soft deleting a category."""
    # Create category
    category_data = QuestionCategoryCreate(name="To Delete", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    # Delete category
    success = await QuestionService.delete_category(db_session, category.id)
    assert success is True

    # Verify it's soft deleted
    deleted_category = await QuestionService.get_category(db_session, category.id)
    assert deleted_category is not None
    assert deleted_category.is_active is False


@pytest.mark.asyncio
async def test_create_question(db_session: AsyncSession):
    """Test creating a question."""
    # Create category first
    category_data = QuestionCategoryCreate(name="Test Category", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    # Create question
    question_data = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="What is ML?",
        options={"A": "Machine Learning", "B": "Deep Learning", "C": "AI", "D": "Data Science"},
        correct_answer={"value": "A"},
        max_score=10,
        difficulty=Difficulty.EASY,
        target_specialties=[Specialty.ML, Specialty.DL],
    )

    question = await QuestionService.create_question(db_session, question_data)

    assert question.id is not None
    assert question.content == "What is ML?"
    assert question.q_type == QuestionType.SINGLE
    assert question.max_score == 10


@pytest.mark.asyncio
async def test_get_question(db_session: AsyncSession):
    """Test getting a question by ID."""
    # Create category and question
    category_data = QuestionCategoryCreate(name="Test Category", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    question_data = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.MULTIPLE,
        content="Select ML algorithms",
        options={"A": "Linear Regression", "B": "CNN", "C": "RNN", "D": "All of above"},
        correct_answer={"value": ["A", "B", "C"]},
        max_score=15,
        difficulty=Difficulty.MEDIUM,
    )

    created_question = await QuestionService.create_question(db_session, question_data)

    # Get question
    retrieved_question = await QuestionService.get_question(db_session, created_question.id)

    assert retrieved_question is not None
    assert retrieved_question.id == created_question.id
    assert retrieved_question.content == "Select ML algorithms"


@pytest.mark.asyncio
async def test_list_questions_with_filters(db_session: AsyncSession):
    """Test listing questions with filters."""
    # Create category
    category_data = QuestionCategoryCreate(name="Filtered Category", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    # Create questions with different types
    for q_type in [QuestionType.SINGLE, QuestionType.MULTIPLE, QuestionType.SHORT]:
        question_data = QuestionCreate(
            category_id=category.id,
            q_type=q_type,
            content=f"Question for {q_type.value}",
            max_score=10,
        )
        await QuestionService.create_question(db_session, question_data)

    # Filter by question type
    questions, total = await QuestionService.list_questions(
        db_session, q_type=QuestionType.SINGLE, active_only=True
    )

    assert total >= 1
    assert all(q.q_type == QuestionType.SINGLE for q in questions)


@pytest.mark.asyncio
async def test_update_question(db_session: AsyncSession):
    """Test updating a question."""
    # Create category and question
    category_data = QuestionCategoryCreate(name="Test Category", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    question_data = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.SHORT,
        content="Original question",
        max_score=10,
    )

    question = await QuestionService.create_question(db_session, question_data)

    # Update question
    update_data = QuestionUpdate(content="Updated question", max_score=15)
    updated_question = await QuestionService.update_question(db_session, question.id, update_data)

    assert updated_question is not None
    assert updated_question.content == "Updated question"
    assert updated_question.max_score == 15


@pytest.mark.asyncio
async def test_delete_question(db_session: AsyncSession):
    """Test soft deleting a question."""
    # Create category and question
    category_data = QuestionCategoryCreate(name="Test Category", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    question_data = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.ESSAY,
        content="To be deleted",
        max_score=20,
    )

    question = await QuestionService.create_question(db_session, question_data)

    # Delete question
    success = await QuestionService.delete_question(db_session, question.id)
    assert success is True

    # Verify it's soft deleted
    deleted_question = await QuestionService.get_question(db_session, question.id)
    assert deleted_question is not None
    assert deleted_question.is_active is False


@pytest.mark.asyncio
async def test_get_questions_by_specialties(db_session: AsyncSession):
    """Test getting questions filtered by specialties."""
    # Create category
    category_data = QuestionCategoryCreate(name="Specialty Category", weight=10)
    category = await QuestionService.create_category(db_session, category_data)

    # Create questions with different target specialties
    question_data_ml = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="ML specific question",
        target_specialties=[Specialty.ML],
        max_score=10,
    )
    await QuestionService.create_question(db_session, question_data_ml)

    question_data_dl = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="DL specific question",
        target_specialties=[Specialty.DL],
        max_score=10,
    )
    await QuestionService.create_question(db_session, question_data_dl)

    # Question with no specialty restriction
    question_data_general = QuestionCreate(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="General question",
        target_specialties=None,
        max_score=10,
    )
    await QuestionService.create_question(db_session, question_data_general)

    # Get questions for ML specialty
    ml_questions = await QuestionService.get_questions_by_specialties(
        db_session, [Specialty.ML], active_only=True
    )

    # Should get ML specific question + general question (no restriction)
    assert len(ml_questions) >= 2
    assert any(q.content == "ML specific question" for q in ml_questions)
