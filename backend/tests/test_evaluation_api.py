"""Integration tests for Evaluation API."""
import pytest
from httpx import AsyncClient
from uuid import uuid4

from src.app.models.answer import AnswerStatus
from src.app.models.question import QuestionType, Difficulty


@pytest.mark.asyncio
async def test_create_answer(
    async_client: AsyncClient, user_token_headers: dict, test_expert_id: str, operator_token_headers: dict
):
    """Test creating an answer via API."""
    # Create category and question first
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SHORT",
            "content": "What is machine learning?",
            "max_score": 10,
            "difficulty": "MEDIUM",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Create answer
    response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"text": "Machine learning is..."},
        },
        headers=user_token_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["expert_id"] == test_expert_id
    assert data["question_id"] == str(question_id)
    assert data["status"] == "DRAFT"


@pytest.mark.asyncio
async def test_submit_answers(
    async_client: AsyncClient, user_token_headers: dict, test_expert_id: str, operator_token_headers: dict
):
    """Test batch submitting answers via API."""
    # Create category and questions
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question1_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "Q1",
            "options": {"A": "A", "B": "B"},
            "correct_answer": {"value": "A"},
            "max_score": 10,
            "difficulty": "EASY",
        },
        headers=operator_token_headers,
    )
    question1_id = question1_response.json()["id"]

    question2_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "Q2",
            "options": {"A": "A", "B": "B"},
            "correct_answer": {"value": "B"},
            "max_score": 10,
            "difficulty": "EASY",
        },
        headers=operator_token_headers,
    )
    question2_id = question2_response.json()["id"]

    # Submit answers
    response = await async_client.post(
        "/api/v1/evaluation/submit",
        json={
            "answers": [
                {
                    "expert_id": test_expert_id,
                    "question_id": str(question1_id),
                    "response_data": {"value": "A"},
                },
                {
                    "expert_id": test_expert_id,
                    "question_id": str(question2_id),
                    "response_data": {"value": "B"},
                },
            ]
        },
        headers=user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["submitted_count"] == 2
    assert len(data["answer_ids"]) == 2


@pytest.mark.asyncio
async def test_get_answer(
    async_client: AsyncClient, user_token_headers: dict, test_expert_id: str, operator_token_headers: dict
):
    """Test getting an answer via API."""
    # Create category, question, and answer
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "ESSAY",
            "content": "Explain AI",
            "max_score": 20,
            "difficulty": "HARD",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"text": "AI is..."},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]

    # Get answer
    response = await async_client.get(f"/api/v1/evaluation/answers/{answer_id}", headers=user_token_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == answer_id


@pytest.mark.asyncio
async def test_update_answer_draft(
    async_client: AsyncClient, user_token_headers: dict, test_expert_id: str, operator_token_headers: dict
):
    """Test updating a draft answer via API."""
    # Create category, question, and answer
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SHORT",
            "content": "Short answer",
            "max_score": 10,
            "difficulty": "MEDIUM",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"text": "First version"},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]
    original_version = answer_response.json()["version"]

    # Update answer
    response = await async_client.put(
        f"/api/v1/evaluation/answers/{answer_id}",
        json={"response_data": {"text": "Updated version"}},
        headers=user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == original_version + 1
    assert data["response_data"]["text"] == "Updated version"


@pytest.mark.asyncio
async def test_auto_grade_correct(
    async_client: AsyncClient, operator_token_headers: dict, test_expert_id: str, user_token_headers: dict
):
    """Test auto-grading with correct answer via API."""
    # Create category and question
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "What is 2+2?",
            "options": {"A": "3", "B": "4", "C": "5"},
            "correct_answer": {"value": "B"},
            "max_score": 10,
            "difficulty": "EASY",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Create and submit answer
    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"value": "B"},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]

    # Auto-grade
    response = await async_client.post(
        "/api/v1/evaluation/grade/auto",
        json={"answer_id": str(answer_id)},
        headers=operator_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 10.0
    assert data["is_correct"] is True
    assert data["max_score"] == 10


@pytest.mark.asyncio
async def test_auto_grade_incorrect(
    async_client: AsyncClient, operator_token_headers: dict, test_expert_id: str, user_token_headers: dict
):
    """Test auto-grading with incorrect answer via API."""
    # Create category and question
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "What is 2+2?",
            "options": {"A": "3", "B": "4", "C": "5"},
            "correct_answer": {"value": "B"},
            "max_score": 10,
            "difficulty": "EASY",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Create and submit answer with incorrect response
    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"value": "A"},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]

    # Auto-grade
    response = await async_client.post(
        "/api/v1/evaluation/grade/auto",
        json={"answer_id": str(answer_id)},
        headers=operator_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 0.0
    assert data["is_correct"] is False


@pytest.mark.asyncio
async def test_manual_grade(
    async_client: AsyncClient, operator_token_headers: dict, test_expert_id: str, user_token_headers: dict
):
    """Test manual grading via API."""
    # Create category and question
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "ESSAY",
            "content": "Explain deep learning",
            "max_score": 20,
            "difficulty": "HARD",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Create and submit answer
    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"text": "Deep learning is..."},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]

    # Manual grade
    response = await async_client.post(
        f"/api/v1/evaluation/grade/{answer_id}/manual",
        json={"score": 15.0, "grader_comment": "Good explanation"},
        headers=operator_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 15.0
    assert data["max_score"] == 20
    assert data["grader_comment"] == "Good explanation"


@pytest.mark.asyncio
async def test_get_expert_answers(
    async_client: AsyncClient, user_token_headers: dict, test_expert_id: str, operator_token_headers: dict
):
    """Test getting all answers for an expert via API."""
    # Create category and questions
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    for i in range(2):
        question_response = await async_client.post(
            "/api/v1/questions",
            json={
                "category_id": str(category_id),
                "q_type": "SINGLE",
                "content": f"Q{i}",
                "options": {"A": "A", "B": "B"},
                "correct_answer": {"value": "A"},
                "max_score": 10,
                "difficulty": "EASY",
            },
            headers=operator_token_headers,
        )
        question_id = question_response.json()["id"]

        # Create answer
        await async_client.post(
            "/api/v1/evaluation/answers",
            json={
                "expert_id": test_expert_id,
                "question_id": str(question_id),
                "response_data": {"value": "A"},
            },
            headers=user_token_headers,
        )

    # Get expert answers
    response = await async_client.get(
        f"/api/v1/evaluation/experts/{test_expert_id}/answers",
        headers=user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["expert_id"] == test_expert_id
    assert data["total_questions"] >= 2
    assert "answers" in data


@pytest.mark.asyncio
async def test_batch_auto_grade(
    async_client: AsyncClient, operator_token_headers: dict, test_expert_id: str, user_token_headers: dict
):
    """Test batch auto-grading for an expert via API."""
    # Create category and questions
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    for i in range(2):
        question_response = await async_client.post(
            "/api/v1/questions",
            json={
                "category_id": str(category_id),
                "q_type": "SINGLE",
                "content": f"Q{i}",
                "options": {"A": "A", "B": "B"},
                "correct_answer": {"value": "A"},
                "max_score": 10,
                "difficulty": "EASY",
            },
            headers=operator_token_headers,
        )
        question_id = question_response.json()["id"]

        # Create and submit answer
        await async_client.post(
            "/api/v1/evaluation/answers",
            json={
                "expert_id": test_expert_id,
                "question_id": str(question_id),
                "response_data": {"value": "A"},
            },
            headers=user_token_headers,
        )

    # Batch auto-grade
    response = await async_client.post(
        f"/api/v1/evaluation/grade/batch/{test_expert_id}",
        headers=operator_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["expert_id"] == test_expert_id
    assert "total_score" in data
    assert "max_total_score" in data


@pytest.mark.asyncio
async def test_auto_grade_subjective_fails(
    async_client: AsyncClient, operator_token_headers: dict, test_expert_id: str, user_token_headers: dict
):
    """Test that auto-grading fails for subjective questions."""
    # Create category and essay question
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "ESSAY",
            "content": "Essay question",
            "max_score": 20,
            "difficulty": "HARD",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Create answer
    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"text": "Answer text"},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]

    # Attempt auto-grade should fail
    response = await async_client.post(
        "/api/v1/evaluation/grade/auto",
        json={"answer_id": str(answer_id)},
        headers=operator_token_headers,
    )

    assert response.status_code == 400
    assert "cannot be auto-graded" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_grading(
    async_client: AsyncClient, user_token_headers: dict, test_expert_id: str, operator_token_headers: dict
):
    """Test that regular users cannot perform grading."""
    # Create category, question, and answer
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    question_response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "Q",
            "options": {"A": "A", "B": "B"},
            "correct_answer": {"value": "A"},
            "max_score": 10,
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    answer_response = await async_client.post(
        "/api/v1/evaluation/answers",
        json={
            "expert_id": test_expert_id,
            "question_id": str(question_id),
            "response_data": {"value": "A"},
        },
        headers=user_token_headers,
    )
    answer_id = answer_response.json()["id"]

    # Regular user cannot auto-grade
    response = await async_client.post(
        "/api/v1/evaluation/grade/auto",
        json={"answer_id": str(answer_id)},
        headers=user_token_headers,
    )

    assert response.status_code == 403  # Forbidden
