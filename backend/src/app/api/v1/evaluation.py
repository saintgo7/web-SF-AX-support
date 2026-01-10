"""Evaluation API endpoints for answers and grading."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_active_user, get_current_operator, get_db
from src.app.models.user import User
from src.app.models.answer import Answer, AnswerStatus
from src.app.schemas.answer import (
    Answer as AnswerSchema,
    AnswerCreate,
    AnswerUpdate,
    AutoGradeResponse,
    AutoGradeRequest,
    ManualGradeRequest,
    ManualGradeResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    ExpertAnswersResponse,
)
from src.app.schemas.score import (
    AIGradeRequest,
    AIGradeResponse,
    ExpertScoreResponse,
    GradingProgress,
    GradingStatistics,
    ScoreRecalculateRequest,
    ScoreRecalculateResponse,
)
from src.app.services.grading_service import GradingService

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


# Answer management endpoints
@router.post("/answers", response_model=AnswerSchema, status_code=status.HTTP_201_CREATED)
async def create_answer(
    answer_data: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update an answer (draft mode).

    Args:
        answer_data: Answer creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created or updated answer
    """
    try:
        return await GradingService.submit_answer(
            db=db,
            expert_id=answer_data.expert_id,
            question_id=answer_data.question_id,
            response_data=answer_data.response_data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create answer: {str(e)}",
        )


@router.post("/submit", response_model=AnswerSubmitResponse)
async def submit_answers(
    submit_data: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit multiple answers for evaluation.

    Args:
        submit_data: Batch answer submission data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Submission result with count and answer IDs
    """
    answer_ids = []

    try:
        for answer_data in submit_data.answers:
            answer = await GradingService.submit_answer(
                db=db,
                expert_id=answer_data.expert_id,
                question_id=answer_data.question_id,
                response_data=answer_data.response_data,
            )

            # Update status to SUBMITTED
            answer.status = AnswerStatus.SUBMITTED
            await db.commit()

            answer_ids.append(answer.id)

        return AnswerSubmitResponse(
            submitted_count=len(answer_ids),
            answer_ids=answer_ids,
            message=f"Successfully submitted {len(answer_ids)} answers for evaluation.",
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answers: {str(e)}",
        )


@router.get("/answers/{answer_id}", response_model=AnswerSchema)
async def get_answer(
    answer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get an answer by ID.

    Args:
        answer_id: Answer UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Answer

    Raises:
        HTTPException: If answer not found
    """
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found",
        )

    return answer


@router.put("/answers/{answer_id}", response_model=AnswerSchema)
async def update_answer(
    answer_id: UUID,
    answer_data: AnswerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing answer (only in DRAFT status).

    Args:
        answer_id: Answer UUID
        answer_data: Answer update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated answer

    Raises:
        HTTPException: If answer not found or not in draft status
    """
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found",
        )

    if answer.status != AnswerStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update answer that is not in DRAFT status",
        )

    # Update fields
    if answer_data.response_data is not None:
        answer.response_data = answer_data.response_data
        answer.version += 1

    if answer_data.status is not None:
        answer.status = answer_data.status

    await db.commit()
    await db.refresh(answer)

    return answer


@router.get("/experts/{expert_id}/answers", response_model=ExpertAnswersResponse)
async def get_expert_answers(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all answers for an expert with summary statistics.

    Args:
        expert_id: Expert UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Expert answers with summary
    """
    # Get all answers for the expert
    result = await db.execute(
        select(Answer).where(Answer.expert_id == expert_id).order_by(Answer.created_at)
    )
    answers = list(result.scalars().all())

    # Get summary
    summary = await GradingService.get_expert_answers_summary(db, expert_id)

    return ExpertAnswersResponse(
        expert_id=expert_id,
        total_questions=len(answers),
        answered_count=summary["answered_count"],
        total_score=summary.get("total_score"),
        max_total_score=summary["max_total_score"],
        answers=answers,
    )


# Grading endpoints
@router.post("/grade/auto", response_model=AutoGradeResponse)
async def auto_grade(
    request: AutoGradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Automatically grade an objective question answer.

    Only SINGLE and MULTIPLE choice questions can be auto-graded.

    Args:
        request: Auto grade request
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Grading result

    Raises:
        HTTPException: If answer not found or not auto-gradable
    """
    try:
        return await GradingService.auto_grade_answer(db, request.answer_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-grading failed: {str(e)}",
        )


@router.post("/grade/{answer_id}/manual", response_model=ManualGradeResponse)
async def manual_grade(
    answer_id: UUID,
    grade_data: ManualGradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Manually grade a subjective question answer.

    Used for SHORT, ESSAY, and FILE type questions.

    Args:
        answer_id: Answer UUID
        grade_data: Manual grading data
        db: Database session
        current_user: Current authenticated operator (grader)

    Returns:
        Grading result

    Raises:
        HTTPException: If answer not found or validation fails
    """
    try:
        answer = await GradingService.manual_grade_answer(
            db=db, answer_id=answer_id, grader_id=current_user.id, grade_data=grade_data
        )

        return ManualGradeResponse(
            answer_id=answer.id,
            score=answer.score,
            max_score=answer.max_score,
            grader_comment=answer.grader_comment,
            graded_at=answer.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Manual grading failed: {str(e)}",
        )


@router.post("/grade/batch/{expert_id}", response_model=ExpertAnswersResponse)
async def batch_auto_grade_expert_answers(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Auto-grade all objective question answers for an expert.

    Processes all SUBMITTED answers that are objective type (SINGLE/MULTIPLE choice).

    Args:
        expert_id: Expert UUID
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Updated expert answers with scores
    """
    from src.app.models.question import Question, QuestionType

    # Get all submitted answers for this expert
    result = await db.execute(
        select(Answer, Question)
        .join(Question, Answer.question_id == Question.id)
        .where(
            and_(
                Answer.expert_id == expert_id,
                Answer.status == AnswerStatus.SUBMITTED,
                Question.q_type.in_([QuestionType.SINGLE, QuestionType.MULTIPLE]),
            )
        )
    )

    rows = result.all()
    graded_count = 0

    for answer, question in rows:
        try:
            await GradingService.auto_grade_answer(db, answer.id)
            graded_count += 1
        except Exception:
            # Skip failed gradings and continue
            pass

    # Get updated summary
    summary = await GradingService.get_expert_answers_summary(db, expert_id)

    # Get all answers
    answers_result = await db.execute(
        select(Answer).where(Answer.expert_id == expert_id).order_by(Answer.created_at)
    )
    answers = list(answers_result.scalars().all())

    return ExpertAnswersResponse(
        expert_id=expert_id,
        total_questions=len(answers),
        answered_count=summary["answered_count"],
        total_score=summary.get("total_score"),
        max_total_score=summary["max_total_score"],
        answers=answers,
    )


# Pending answers for grading
@router.get("/pending-answers", response_model=list[AnswerSchema])
async def get_pending_answers(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get all submitted answers pending grading.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current operator (grader)

    Returns:
        List of answers awaiting grading
    """
    result = await db.execute(
        select(Answer)
        .where(Answer.status == AnswerStatus.SUBMITTED)
        .order_by(Answer.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/pending-by-expert", response_model=list[dict])
async def get_pending_by_expert(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get pending answers grouped by expert.

    Returns a list of experts with their pending answers.

    Args:
        db: Database session
        current_user: Current operator (grader)

    Returns:
        List of experts with pending answer counts and details
    """
    from src.app.models.expert import Expert
    from src.app.models.question import Question

    # Get all submitted answers with expert and question info
    result = await db.execute(
        select(Answer, Expert, Question)
        .join(Expert, Answer.expert_id == Expert.id)
        .join(Question, Answer.question_id == Question.id)
        .where(Answer.status == AnswerStatus.SUBMITTED)
        .order_by(Expert.id, Answer.created_at)
    )

    rows = result.all()

    # Group by expert
    experts_data: dict = {}
    for answer, expert, question in rows:
        expert_id = str(expert.id)
        if expert_id not in experts_data:
            experts_data[expert_id] = {
                "expert_id": expert_id,
                "expert_name": expert.user.name if expert.user else "Unknown",
                "pending_count": 0,
                "total_max_score": 0,
                "answers": [],
            }

        experts_data[expert_id]["pending_count"] += 1
        experts_data[expert_id]["total_max_score"] += question.max_score
        experts_data[expert_id]["answers"].append({
            "answer_id": str(answer.id),
            "question_id": str(question.id),
            "question_content": question.content,
            "question_type": question.q_type.value if hasattr(question.q_type, 'value') else question.q_type,
            "max_score": question.max_score,
            "response_data": answer.response_data,
            "created_at": answer.created_at.isoformat(),
        })

    return list(experts_data.values())


# AI-assisted grading endpoints
@router.post("/grade/ai", response_model=AIGradeResponse)
async def ai_grade_answer(
    request: AIGradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get AI-assisted grading suggestion for a subjective question.

    This provides a suggested score and reasoning based on keyword matching
    and rubric analysis. The evaluator can accept, modify, or reject the suggestion.

    Args:
        request: AI grade request with answer_id
        db: Database session
        current_user: Current authenticated operator

    Returns:
        AI grading suggestion with confidence score and reasoning

    Raises:
        HTTPException: If answer not found or not gradable
    """
    try:
        result = await GradingService.ai_grade_subjective(db, request.answer_id)
        return AIGradeResponse(
            answer_id=result["answer_id"],
            question_id=result["question_id"],
            suggested_score=result["suggested_score"],
            max_score=result["max_score"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            matched_keywords=result["matched_keywords"],
            rubric_coverage=result["rubric_coverage"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI grading failed: {str(e)}",
        )


# Score endpoints
@router.get("/scores/{expert_id}", response_model=ExpertScoreResponse)
async def get_expert_score(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get aggregated scores for an expert.

    Returns the total score, category breakdown, and ranking information.
    Triggers recalculation if scores are stale.

    Args:
        expert_id: Expert UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Expert score with category breakdown

    Raises:
        HTTPException: If expert not found
    """
    from src.app.models.expert import Expert
    from src.app.models.expert_score import ExpertScore
    from src.app.schemas.score import CategoryScoreSummary

    # Verify expert exists
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found",
        )

    # Get or calculate expert score
    try:
        score_data = await GradingService.calculate_expert_total_score(db, expert_id)

        # Get the expert_score record for ID and timestamps
        score_result = await db.execute(
            select(ExpertScore).where(ExpertScore.expert_id == expert_id)
        )
        expert_score = score_result.scalar_one_or_none()

        if not expert_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expert score not calculated yet",
            )

        # Convert category_scores from dict to list of CategoryScoreSummary
        category_scores_list = []
        for cat_id, cat_data in expert_score.category_scores.items():
            category_scores_list.append(
                CategoryScoreSummary(
                    category_id=UUID(cat_id),
                    category_name=cat_data.get("category_name", "Unknown"),
                    score=cat_data.get("score", 0),
                    max_score=cat_data.get("max_score", 0),
                    percentage=cat_data.get("percentage", 0),
                    graded_count=cat_data.get("graded_count", 0),
                    total_count=cat_data.get("total_count", 0),
                )
            )

        return ExpertScoreResponse(
            id=expert_score.id,
            expert_id=expert_score.expert_id,
            total_score=expert_score.total_score,
            max_possible_score=expert_score.max_possible_score,
            average_percentage=expert_score.average_percentage,
            graded_count=expert_score.graded_count,
            total_count=expert_score.total_count,
            category_scores=category_scores_list,
            rank=expert_score.rank,
            percentile=expert_score.percentile,
            last_calculated_at=expert_score.last_calculated_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expert score: {str(e)}",
        )


@router.post("/scores/{expert_id}/recalculate", response_model=ScoreRecalculateResponse)
async def recalculate_expert_score(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Force recalculation of an expert's aggregated scores.

    Useful after bulk grading operations or data corrections.

    Args:
        expert_id: Expert UUID
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Score recalculation result with before/after comparison
    """
    from src.app.models.expert_score import ExpertScore

    # Get previous score
    result = await db.execute(
        select(ExpertScore).where(ExpertScore.expert_id == expert_id)
    )
    prev_score = result.scalar_one_or_none()

    previous_score = prev_score.total_score if prev_score else 0.0
    previous_percentage = prev_score.average_percentage if prev_score else 0.0

    try:
        # Recalculate
        await GradingService.calculate_expert_total_score(db, expert_id)

        # Get new score
        result = await db.execute(
            select(ExpertScore).where(ExpertScore.expert_id == expert_id)
        )
        new_score_record = result.scalar_one()

        return ScoreRecalculateResponse(
            expert_id=expert_id,
            previous_score=previous_score,
            new_score=new_score_record.total_score,
            previous_percentage=previous_percentage,
            new_percentage=new_score_record.average_percentage,
            recalculated_at=new_score_record.last_calculated_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Score recalculation failed: {str(e)}",
        )


@router.get("/progress/{expert_id}", response_model=GradingProgress)
async def get_grading_progress(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get grading progress for an expert.

    Returns counts of answers by status and overall progress percentage.

    Args:
        expert_id: Expert UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Grading progress statistics
    """
    try:
        progress = await GradingService.get_grading_progress(db, expert_id)
        return GradingProgress(**progress)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get grading progress: {str(e)}",
        )


@router.get("/statistics", response_model=GradingStatistics)
async def get_grading_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get overall grading statistics for the evaluator dashboard.

    Returns aggregate statistics across all experts and answers.

    Args:
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Overall grading statistics
    """
    try:
        stats = await GradingService.get_grading_statistics(db)
        return GradingStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )
