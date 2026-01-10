"""Integration tests for Questions API."""
import pytest
from httpx import AsyncClient
from uuid import uuid4

from src.app.models.question import QuestionType, Difficulty, Specialty


@pytest.mark.asyncio
async def test_create_category(async_client: AsyncClient, operator_token_headers: dict):
    """Test creating a question category via API."""
    response = await async_client.post(
        "/api/v1/questions/categories",
        json={
            "name": "Machine Learning Basics",
            "description": "Fundamental ML concepts",
            "weight": 20,
            "display_order": 1,
            "is_active": True,
        },
        headers=operator_token_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Machine Learning Basics"
    assert data["weight"] == 20
    assert "id" in data


@pytest.mark.asyncio
async def test_list_categories(async_client: AsyncClient):
    """Test listing question categories via API."""
    response = await async_client.get("/api/v1/questions/categories")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_category(async_client: AsyncClient, operator_token_headers: dict):
    """Test getting a specific category via API."""
    # First create a category
    create_response = await async_client.post(
        "/api/v1/questions/categories",
        json={
            "name": "Deep Learning",
            "description": "Advanced neural networks",
            "weight": 15,
        },
        headers=operator_token_headers,
    )

    category_id = create_response.json()["id"]

    # Get the category
    response = await async_client.get(f"/api/v1/questions/categories/{category_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Deep Learning"


@pytest.mark.asyncio
async def test_update_category(async_client: AsyncClient, operator_token_headers: dict):
    """Test updating a category via API."""
    # Create category
    create_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Original Name", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = create_response.json()["id"]

    # Update category
    response = await async_client.put(
        f"/api/v1/questions/categories/{category_id}",
        json={"name": "Updated Name", "weight": 20},
        headers=operator_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["weight"] == 20


@pytest.mark.asyncio
async def test_delete_category(async_client: AsyncClient, operator_token_headers: dict):
    """Test deleting a category via API."""
    # Create category
    create_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "To Delete", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = create_response.json()["id"]

    # Delete category
    response = await async_client.delete(
        f"/api/v1/questions/categories/{category_id}",
        headers=operator_token_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_question(async_client: AsyncClient, operator_token_headers: dict):
    """Test creating a question via API."""
    # Create category first
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Test Category", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    # Create question
    response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "What is the capital of France?",
            "options": {"A": "London", "B": "Paris", "C": "Berlin", "D": "Madrid"},
            "correct_answer": {"value": "B"},
            "max_score": 10,
            "difficulty": "EASY",
            "target_specialties": ["ML", "DL"],
            "explanation": "Paris is the capital of France",
        },
        headers=operator_token_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "What is the capital of France?"
    assert data["q_type"] == "SINGLE"
    assert data["max_score"] == 10


@pytest.mark.asyncio
async def test_list_questions(async_client: AsyncClient):
    """Test listing questions via API."""
    response = await async_client.get("/api/v1/questions")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


@pytest.mark.asyncio
async def test_list_questions_with_filters(async_client: AsyncClient):
    """Test listing questions with filters via API."""
    response = await async_client.get(
        "/api/v1/questions?q_type=SINGLE&difficulty=EASY&skip=0&limit=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # All returned questions should match the filter
    for item in data["items"]:
        assert item["q_type"] == "SINGLE"


@pytest.mark.asyncio
async def test_get_question(async_client: AsyncClient, operator_token_headers: dict):
    """Test getting a specific question via API."""
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
            "q_type": "MULTIPLE",
            "content": "Select all prime numbers",
            "options": {"A": "2", "B": "4", "C": "5", "D": "6"},
            "correct_answer": {"value": ["A", "C"]},
            "max_score": 15,
            "difficulty": "MEDIUM",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Get question
    response = await async_client.get(f"/api/v1/questions/{question_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == question_id
    assert data["content"] == "Select all prime numbers"


@pytest.mark.asyncio
async def test_update_question(async_client: AsyncClient, operator_token_headers: dict):
    """Test updating a question via API."""
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
            "q_type": "SHORT",
            "content": "Original question",
            "max_score": 10,
            "difficulty": "MEDIUM",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Update question
    response = await async_client.put(
        f"/api/v1/questions/{question_id}",
        json={
            "content": "Updated question",
            "max_score": 15,
        },
        headers=operator_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated question"
    assert data["max_score"] == 15


@pytest.mark.asyncio
async def test_delete_question(async_client: AsyncClient, operator_token_headers: dict):
    """Test deleting a question via API."""
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
            "content": "To be deleted",
            "max_score": 20,
            "difficulty": "HARD",
        },
        headers=operator_token_headers,
    )
    question_id = question_response.json()["id"]

    # Delete question
    response = await async_client.delete(
        f"/api/v1/questions/{question_id}",
        headers=operator_token_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_questions_by_specialties(async_client: AsyncClient, operator_token_headers: dict):
    """Test getting questions filtered by specialties via API."""
    # Create category
    category_response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Specialty Test", "weight": 10},
        headers=operator_token_headers,
    )
    category_id = category_response.json()["id"]

    # Create ML-specific question
    await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "ML specific",
            "target_specialties": ["ML"],
            "max_score": 10,
        },
        headers=operator_token_headers,
    )

    # Create general question (no specialty restriction)
    await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(category_id),
            "q_type": "SINGLE",
            "content": "General question",
            "target_specialties": None,
            "max_score": 10,
        },
        headers=operator_token_headers,
    )

    # Get questions for ML specialty
    response = await async_client.get("/api/v1/questions/by-specialties/ML")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should include both ML-specific and general questions
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_unauthorized_category_creation(async_client: AsyncClient, user_token_headers: dict):
    """Test that non-operators cannot create categories."""
    response = await async_client.post(
        "/api/v1/questions/categories",
        json={"name": "Unauthorized", "weight": 10},
        headers=user_token_headers,
    )

    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_unauthorized_question_creation(async_client: AsyncClient, user_token_headers: dict):
    """Test that non-operators cannot create questions."""
    response = await async_client.post(
        "/api/v1/questions",
        json={
            "category_id": str(uuid4()),
            "q_type": "SINGLE",
            "content": "Unauthorized",
            "max_score": 10,
        },
        headers=user_token_headers,
    )

    assert response.status_code == 403  # Forbidden
