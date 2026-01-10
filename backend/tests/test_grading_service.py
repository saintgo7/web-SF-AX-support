"""Unit tests for Grading Service."""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.answer import Answer, AnswerStatus
from src.app.models.expert import Expert
from src.app.models.question import Question, QuestionCategory, QuestionType, Difficulty
from src.app.schemas.answer import ManualGradeRequest
from src.app.services.grading_service import GradingService


@pytest.mark.asyncio
async def test_auto_grade_single_choice_correct(db_session: AsyncSession, test_expert: Expert):
    """Test auto-grading a single choice question with correct answer."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create single choice question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="What is 2+2?",
        options={"A": "3", "B": "4", "C": "5", "D": "6"},
        correct_answer={"value": "B"},
        max_score=10,
        difficulty=Difficulty.EASY,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer with correct response
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"value": "B"},
        max_score=10,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Auto-grade
    result = await GradingService.auto_grade_answer(db_session, answer.id)

    assert result.score == 10.0
    assert result.is_correct is True
    assert result.max_score == 10


@pytest.mark.asyncio
async def test_auto_grade_single_choice_incorrect(db_session: AsyncSession, test_expert: Expert):
    """Test auto-grading a single choice question with incorrect answer."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create single choice question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="What is 2+2?",
        options={"A": "3", "B": "4", "C": "5", "D": "6"},
        correct_answer={"value": "B"},
        max_score=10,
        difficulty=Difficulty.EASY,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer with incorrect response
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"value": "A"},
        max_score=10,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Auto-grade
    result = await GradingService.auto_grade_answer(db_session, answer.id)

    assert result.score == 0.0
    assert result.is_correct is False
    assert "오답" in result.feedback


@pytest.mark.asyncio
async def test_auto_grade_multiple_choice_correct(db_session: AsyncSession, test_expert: Expert):
    """Test auto-grading a multiple choice question with correct answers."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create multiple choice question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.MULTIPLE,
        content="Select all even numbers",
        options={"A": "2", "B": "3", "C": "4", "D": "5"},
        correct_answer={"value": ["A", "C"]},
        max_score=10,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer with correct responses
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"value": ["A", "C"]},
        max_score=10,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Auto-grade
    result = await GradingService.auto_grade_answer(db_session, answer.id)

    assert result.score == 10.0
    assert result.is_correct is True


@pytest.mark.asyncio
async def test_auto_grade_multiple_choice_partial(db_session: AsyncSession, test_expert: Expert):
    """Test auto-grading a multiple choice question with partial correct answers."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create multiple choice question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.MULTIPLE,
        content="Select all even numbers",
        options={"A": "2", "B": "3", "C": "4", "D": "5"},
        correct_answer={"value": ["A", "C"]},
        max_score=10,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer with only one correct selection
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"value": ["A"]},
        max_score=10,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Auto-grade
    result = await GradingService.auto_grade_answer(db_session, answer.id)

    # Should get partial credit (5 out of 10)
    assert result.score > 0
    assert result.score < 10
    assert result.is_correct is False
    assert "부분 정답" in result.feedback


@pytest.mark.asyncio
async def test_auto_grade_subjective_fails(db_session: AsyncSession, test_expert: Expert):
    """Test that auto-grading fails for subjective questions."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create essay question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.ESSAY,
        content="Explain machine learning",
        max_score=20,
        difficulty=Difficulty.HARD,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"text": "ML is..."},
        max_score=20,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Attempt auto-grade should fail
    with pytest.raises(ValueError, match="cannot be auto-graded"):
        await GradingService.auto_grade_answer(db_session, answer.id)


@pytest.mark.asyncio
async def test_manual_grade(db_session: AsyncSession, test_expert: Expert, test_user):
    """Test manual grading of a subjective question."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create essay question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.ESSAY,
        content="Explain deep learning",
        max_score=20,
        difficulty=Difficulty.HARD,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"text": "Deep learning is..."},
        max_score=20,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Manual grade
    grade_data = ManualGradeRequest(score=15.0, grader_comment="Good explanation")
    graded_answer = await GradingService.manual_grade_answer(
        db_session, answer.id, test_user.id, grade_data
    )

    assert graded_answer.score == 15.0
    assert graded_answer.max_score == 20
    assert graded_answer.grader_id == test_user.id
    assert graded_answer.grader_comment == "Good explanation"
    assert graded_answer.status == AnswerStatus.GRADED


@pytest.mark.asyncio
async def test_manual_grade_exceeds_max(db_session: AsyncSession, test_expert: Expert, test_user):
    """Test that manual grading validates score against max_score."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create question with max_score=10
    question = Question(
        category_id=category.id,
        q_type=QuestionType.SHORT,
        content="Short answer",
        max_score=10,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add(question)
    await db_session.commit()

    # Create answer
    answer = Answer(
        expert_id=test_expert.id,
        question_id=question.id,
        version=1,
        response_data={"text": "Answer"},
        max_score=10,
        status=AnswerStatus.SUBMITTED,
    )
    db_session.add(answer)
    await db_session.commit()

    # Attempt to grade with score exceeding max
    grade_data = ManualGradeRequest(score=15.0)

    with pytest.raises(ValueError, match="exceeds maximum allowed score"):
        await GradingService.manual_grade_answer(db_session, answer.id, test_user.id, grade_data)


@pytest.mark.asyncio
async def test_submit_answer_new(db_session: AsyncSession, test_expert: Expert):
    """Test submitting a new answer."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.SHORT,
        content="Short answer question",
        max_score=10,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add(question)
    await db_session.commit()

    # Submit answer
    answer = await GradingService.submit_answer(
        db_session,
        expert_id=test_expert.id,
        question_id=question.id,
        response_data={"text": "My answer"},
    )

    assert answer.id is not None
    assert answer.version == 1
    assert answer.response_data == {"text": "My answer"}
    assert answer.status == AnswerStatus.DRAFT
    assert answer.max_score == 10


@pytest.mark.asyncio
async def test_submit_answer_update_draft(db_session: AsyncSession, test_expert: Expert):
    """Test updating an existing draft answer."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create question
    question = Question(
        category_id=category.id,
        q_type=QuestionType.SHORT,
        content="Short answer question",
        max_score=10,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add(question)
    await db_session.commit()

    # Submit initial answer
    answer1 = await GradingService.submit_answer(
        db_session,
        expert_id=test_expert.id,
        question_id=question.id,
        response_data={"text": "First answer"},
    )

    # Update answer (should increment version)
    answer2 = await GradingService.submit_answer(
        db_session,
        expert_id=test_expert.id,
        question_id=question.id,
        response_data={"text": "Updated answer"},
    )

    assert answer2.id == answer1.id
    assert answer2.version == 2
    assert answer2.response_data == {"text": "Updated answer"}


@pytest.mark.asyncio
async def test_get_expert_answers_summary(db_session: AsyncSession, test_expert: Expert):
    """Test getting expert answers summary."""
    # Create category
    category = QuestionCategory(name="Test", weight=10)
    db_session.add(category)
    await db_session.commit()

    # Create questions
    question1 = Question(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="Q1",
        max_score=10,
        difficulty=Difficulty.EASY,
    )
    question2 = Question(
        category_id=category.id,
        q_type=QuestionType.SINGLE,
        content="Q2",
        max_score=20,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add_all([question1, question2])
    await db_session.commit()

    # Create graded answers
    answer1 = Answer(
        expert_id=test_expert.id,
        question_id=question1.id,
        version=1,
        response_data={"value": "A"},
        max_score=10,
        score=10.0,
        status=AnswerStatus.GRADED,
    )
    answer2 = Answer(
        expert_id=test_expert.id,
        question_id=question2.id,
        version=1,
        response_data={"value": "B"},
        max_score=20,
        score=15.0,
        status=AnswerStatus.GRADED,
    )
    db_session.add_all([answer1, answer2])
    await db_session.commit()

    # Get summary
    summary = await GradingService.get_expert_answers_summary(db_session, test_expert.id)

    assert summary["answered_count"] == 2
    assert summary["total_score"] == 25.0
    assert summary["max_total_score"] == 30
    assert summary["average_score"] == pytest.approx(83.33, rel=0.1)
