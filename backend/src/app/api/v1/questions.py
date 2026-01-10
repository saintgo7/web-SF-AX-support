"""Question management API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_operator, get_db
from src.app.models.user import User
from src.app.models.question import QuestionType, Specialty
from src.app.schemas.question import (
    QuestionCategoryCreate,
    QuestionCategoryUpdate,
    QuestionCategory as QuestionCategorySchema,
    QuestionCreate,
    QuestionUpdate,
    Question as QuestionSchema,
    QuestionQuery,
    QuestionListResponse,
)
from src.app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


# Category endpoints
@router.post("/categories", response_model=QuestionCategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: QuestionCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Create a new question category.

    Args:
        category_data: Category creation data
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Created category
    """
    try:
        return await QuestionService.create_category(db, category_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create category: {str(e)}",
        )


@router.get("/categories", response_model=list[QuestionCategorySchema])
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Only return active categories"),
    db: AsyncSession = Depends(get_db),
):
    """List all question categories with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Only return active categories
        db: Database session

    Returns:
        List of categories
    """
    return await QuestionService.list_categories(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/categories/{category_id}", response_model=QuestionCategorySchema)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a question category by ID.

    Args:
        category_id: Category UUID
        db: Database session

    Returns:
        Category

    Raises:
        HTTPException: If category not found
    """
    category = await QuestionService.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )
    return category


@router.put("/categories/{category_id}", response_model=QuestionCategorySchema)
async def update_category(
    category_id: UUID,
    category_data: QuestionCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Update a question category.

    Args:
        category_id: Category UUID
        category_data: Category update data
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Updated category

    Raises:
        HTTPException: If category not found
    """
    category = await QuestionService.update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Delete a question category (soft delete).

    Args:
        category_id: Category UUID
        db: Database session
        current_user: Current authenticated operator

    Raises:
        HTTPException: If category not found
    """
    success = await QuestionService.delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )


# Question endpoints
@router.post("", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Create a new question.

    Args:
        question_data: Question creation data
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Created question
    """
    try:
        return await QuestionService.create_question(db, question_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create question: {str(e)}",
        )


@router.get("", response_model=QuestionListResponse)
async def list_questions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    category_id: UUID | None = Query(None, description="Filter by category ID"),
    q_type: QuestionType | None = Query(None, description="Filter by question type"),
    specialty: Specialty | None = Query(None, description="Filter by target specialty"),
    active_only: bool = Query(True, description="Only return active questions"),
    db: AsyncSession = Depends(get_db),
):
    """List questions with filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category_id: Filter by category ID
        q_type: Filter by question type
        specialty: Filter by target specialty
        active_only: Only return active questions
        db: Database session

    Returns:
        Paginated list of questions
    """
    questions, total = await QuestionService.list_questions(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        q_type=q_type,
        specialty=specialty,
        active_only=active_only,
    )

    return QuestionListResponse(items=questions, total=total, skip=skip, limit=limit)


@router.get("/{question_id}", response_model=QuestionSchema)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a question by ID.

    Args:
        question_id: Question UUID
        db: Database session

    Returns:
        Question

    Raises:
        HTTPException: If question not found
    """
    question = await QuestionService.get_question(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found",
        )
    return question


@router.put("/{question_id}", response_model=QuestionSchema)
async def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Update a question.

    Args:
        question_id: Question UUID
        question_data: Question update data
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Updated question

    Raises:
        HTTPException: If question not found
    """
    try:
        question = await QuestionService.update_question(db, question_id, question_data)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found",
            )
        return question
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Delete a question (soft delete).

    Args:
        question_id: Question UUID
        db: Database session
        current_user: Current authenticated operator

    Raises:
        HTTPException: If question not found
    """
    success = await QuestionService.delete_question(db, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found",
        )


@router.get("/by-specialties/{specialties}", response_model=list[QuestionSchema])
async def get_questions_by_specialties(
    specialties: str,  # Comma-separated list
    db: AsyncSession = Depends(get_db),
):
    """Get questions filtered by expert specialties.

    This endpoint is used to dynamically generate evaluation questions
    based on an expert's declared specialties.

    Args:
        specialties: Comma-separated list of specialty values (e.g., "ML,DL,CV")
        db: Database session

    Returns:
        List of matching questions
    """
    try:
        specialty_list = [Specialty(s.strip()) for s in specialties.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid specialty values. Valid values: {[s.value for s in Specialty]}",
        )

    questions = await QuestionService.get_questions_by_specialties(db, specialty_list)
    return questions
