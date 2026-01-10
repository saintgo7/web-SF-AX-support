"""Grading service for auto-grading and evaluation logic."""
import re
from datetime import datetime, date
from typing import Any
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.answer import Answer, AnswerStatus
from src.app.models.question import Question, QuestionType, QuestionCategory
from src.app.models.expert import Expert
from src.app.models.expert_score import ExpertScore
from src.app.schemas.answer import AutoGradeResponse, ManualGradeRequest
from src.app.schemas.score import (
    AIGradeResponse,
    CategoryScoreSummary,
    ExpertScoreResponse,
    GradingStatistics,
    GradingProgress,
)


class GradingService:
    """Service for grading answers."""

    @staticmethod
    async def auto_grade_answer(db: AsyncSession, answer_id: Any) -> AutoGradeResponse:
        """Automatically grade an objective question answer.

        Args:
            db: Database session
            answer_id: Answer UUID

        Returns:
            Grading result

        Raises:
            ValueError: If answer not found or question type not auto-gradable
        """
        # Get answer with question
        result = await db.execute(
            select(Answer, Question)
            .join(Question, Answer.question_id == Question.id)
            .where(Answer.id == answer_id)
        )
        row = result.one_or_none()
        if not row:
            raise ValueError(f"Answer {answer_id} not found")

        answer, question = row

        # Check if question type is auto-gradable
        if question.q_type not in [QuestionType.SINGLE, QuestionType.MULTIPLE]:
            raise ValueError(
                f"Question type {question.q_type.value} cannot be auto-graded. "
                "Only SINGLE and MULTIPLE choice questions are supported."
            )

        # Perform auto-grading
        score = 0.0
        is_correct = False
        feedback = None

        if question.q_type == QuestionType.SINGLE:
            # Single choice: exact match required
            user_value = answer.response_data.get("value")
            correct_value = question.correct_answer.get("value") if question.correct_answer else None

            if user_value and user_value == correct_value:
                score = float(question.max_score)
                is_correct = True
                feedback = "정답입니다." if question.explanation is None else question.explanation
            else:
                score = 0.0
                is_correct = False
                feedback = f"오답입니다. 정답: {correct_value}" if correct_value else "오답입니다."

        elif question.q_type == QuestionType.MULTIPLE:
            # Multiple choice: all correct options must be selected, no incorrect options
            user_values = set(answer.response_data.get("value", []))
            correct_values = set(question.correct_answer.get("value", [])) if question.correct_answer else set()

            if user_values == correct_values and len(correct_values) > 0:
                score = float(question.max_score)
                is_correct = True
                feedback = "정답입니다." if question.explanation is None else question.explanation
            else:
                # Partial scoring: give partial credit for partially correct answers
                if correct_values:
                    correct_selected = len(user_values & correct_values)
                    incorrect_selected = len(user_values - correct_values)
                    total_correct = len(correct_values)

                    # Simple scoring: correct selections earn points, wrong selections lose points
                    if incorrect_selected == 0 and correct_selected > 0:
                        score = (correct_selected / total_correct) * question.max_score
                        feedback = (
                            f"부분 정답 ({correct_selected}/{total_correct}). "
                            f"취득 점수: {score:.1f}/{question.max_score}"
                        )
                    else:
                        score = 0.0
                        feedback = (
                            f"오답입니다. 선택한 답안에 오답이 포함되어 있습니다. "
                            f"정답: {', '.join(sorted(correct_values))}"
                        )
                else:
                    score = 0.0
                    is_correct = False
                    feedback = "오답입니다."

        # Update answer
        answer.score = score
        answer.max_score = question.max_score
        answer.is_correct = is_correct
        answer.status = AnswerStatus.GRADED

        await db.commit()

        return AutoGradeResponse(
            answer_id=answer.id,
            score=score,
            max_score=question.max_score,
            is_correct=is_correct,
            feedback=feedback,
        )

    @staticmethod
    async def manual_grade_answer(
        db: AsyncSession, answer_id: Any, grader_id: Any, grade_data: ManualGradeRequest
    ) -> Answer:
        """Manually grade a subjective question answer.

        Args:
            db: Database session
            answer_id: Answer UUID
            grader_id: Grader user UUID
            grade_data: Manual grading data

        Returns:
            Updated answer

        Raises:
            ValueError: If answer not found
        """
        # Get answer
        result = await db.execute(select(Answer).where(Answer.id == answer_id))
        answer = result.scalar_one_or_none()

        if not answer:
            raise ValueError(f"Answer {answer_id} not found")

        # Get question to verify max_score
        question_result = await db.execute(select(Question).where(Question.id == answer.question_id))
        question = question_result.scalar_one_or_none()

        if not question:
            raise ValueError(f"Question {answer.question_id} not found")

        # Validate score
        if grade_data.score > question.max_score:
            raise ValueError(
                f"Score {grade_data.score} exceeds maximum allowed score {question.max_score}"
            )

        # Update answer
        answer.score = grade_data.score
        answer.max_score = question.max_score
        answer.is_correct = None  # Subjective questions don't have is_correct
        answer.grader_id = grader_id
        answer.grader_comment = grade_data.grader_comment
        answer.status = AnswerStatus.GRADED

        await db.commit()
        await db.refresh(answer)

        return answer

    @staticmethod
    async def submit_answer(db: AsyncSession, expert_id: Any, question_id: Any, response_data: dict) -> Answer:
        """Submit or update an answer.

        Args:
            db: Database session
            expert_id: Expert UUID
            question_id: Question UUID
            response_data: Response content

        Returns:
            Created or updated answer
        """
        # Check if answer exists for this expert and question
        result = await db.execute(
            select(Answer).where(
                and_(Answer.expert_id == expert_id, Answer.question_id == question_id, Answer.status == AnswerStatus.DRAFT)
            )
        )
        existing_answer = result.scalar_one_or_none()

        if existing_answer:
            # Update existing answer (version increment)
            existing_answer.version += 1
            existing_answer.response_data = response_data
            await db.commit()
            await db.refresh(existing_answer)
            return existing_answer
        else:
            # Get question to get max_score
            question_result = await db.execute(select(Question).where(Question.id == question_id))
            question = question_result.scalar_one_or_none()

            if not question:
                raise ValueError(f"Question {question_id} not found")

            # Create new answer
            new_answer = Answer(
                expert_id=expert_id,
                question_id=question_id,
                version=1,
                response_data=response_data,
                max_score=question.max_score,
                status=AnswerStatus.DRAFT,
            )
            db.add(new_answer)
            await db.commit()
            await db.refresh(new_answer)
            return new_answer

    @staticmethod
    async def get_expert_answers_summary(db: AsyncSession, expert_id: Any) -> dict[str, Any]:
        """Get summary of all answers for an expert.

        Args:
            db: Database session
            expert_id: Expert UUID

        Returns:
            Summary dict with total_score, answered_count, etc.
        """
        # Get all submitted/graded answers
        result = await db.execute(
            select(Answer).where(
                and_(
                    Answer.expert_id == expert_id,
                    Answer.status.in_([AnswerStatus.SUBMITTED, AnswerStatus.GRADED, AnswerStatus.REVIEWED]),
                )
            )
        )
        answers = list(result.scalars().all())

        total_score = sum(a.score or 0 for a in answers)
        max_total_score = sum(a.max_score for a in answers)

        return {
            "expert_id": str(expert_id),
            "answered_count": len(answers),
            "total_score": total_score,
            "max_total_score": max_total_score,
            "average_score": (total_score / max_total_score * 100) if max_total_score > 0 else 0,
        }

    # ========== Sprint 4: AI-Assisted Grading ==========

    @staticmethod
    async def ai_grade_subjective(db: AsyncSession, answer_id: Any) -> AIGradeResponse:
        """AI-assisted grading for subjective questions (SHORT, ESSAY).

        Uses keyword matching and rubric analysis to suggest a score.

        Args:
            db: Database session
            answer_id: Answer UUID

        Returns:
            AI grading suggestion with confidence and reasoning
        """
        # Get answer with question
        result = await db.execute(
            select(Answer, Question)
            .join(Question, Answer.question_id == Question.id)
            .where(Answer.id == answer_id)
        )
        row = result.one_or_none()
        if not row:
            raise ValueError(f"Answer {answer_id} not found")

        answer, question = row

        # Check if question type is subjective
        if question.q_type not in [QuestionType.SHORT, QuestionType.ESSAY]:
            raise ValueError(
                f"Question type {question.q_type.value} is not subjective. "
                "Use auto_grade_answer for objective questions."
            )

        # Extract answer text
        answer_text = answer.response_data.get("text", "").strip().lower()
        if not answer_text:
            return AIGradeResponse(
                answer_id=answer.id,
                question_id=question.id,
                suggested_score=0.0,
                max_score=float(question.max_score),
                confidence=1.0,
                reasoning="응답이 비어 있습니다.",
                matched_keywords=[],
                rubric_coverage=0.0,
            )

        # Parse scoring rubric
        rubric = question.scoring_rubric or {}
        keywords = rubric.get("keywords", [])
        criteria = rubric.get("criteria", [])

        # Keyword matching
        matched_keywords = []
        for keyword in keywords:
            if isinstance(keyword, str) and keyword.lower() in answer_text:
                matched_keywords.append(keyword)
            elif isinstance(keyword, dict):
                kw = keyword.get("term", "").lower()
                if kw and kw in answer_text:
                    matched_keywords.append(kw)

        # Calculate keyword-based score component
        keyword_score = 0.0
        if keywords:
            keyword_score = (len(matched_keywords) / len(keywords)) * 0.5  # 50% weight

        # Criteria analysis (simplified rule-based)
        criteria_score = 0.0
        criteria_met = 0
        reasoning_parts = []

        for criterion in criteria:
            if isinstance(criterion, dict):
                criterion_text = criterion.get("description", "").lower()
                criterion_keywords = criterion.get("keywords", [])
                criterion_weight = criterion.get("weight", 1.0)

                # Check if any criterion keywords are present
                for ck in criterion_keywords:
                    if ck.lower() in answer_text:
                        criteria_met += 1
                        criteria_score += criterion_weight
                        reasoning_parts.append(f"'{criterion.get('description', 'criterion')}' 충족")
                        break

        if criteria:
            criteria_score = (criteria_score / len(criteria)) * 0.5  # 50% weight

        # Calculate total suggested score
        total_ratio = keyword_score + criteria_score
        suggested_score = total_ratio * question.max_score

        # Calculate confidence based on coverage
        coverage = 0.0
        if keywords or criteria:
            keyword_coverage = len(matched_keywords) / len(keywords) if keywords else 0
            criteria_coverage = criteria_met / len(criteria) if criteria else 0
            coverage = (keyword_coverage + criteria_coverage) / 2 * 100

        # Adjust confidence based on answer length for ESSAY questions
        confidence = 0.7  # Base confidence
        if question.q_type == QuestionType.ESSAY:
            word_count = len(answer_text.split())
            if word_count < 50:
                confidence *= 0.8
                reasoning_parts.append("응답이 짧음 (신뢰도 감소)")
            elif word_count > 200:
                confidence *= 1.1
                if confidence > 1.0:
                    confidence = 1.0

        # Build reasoning
        if matched_keywords:
            reasoning_parts.insert(0, f"키워드 매칭: {len(matched_keywords)}/{len(keywords)}")
        if not reasoning_parts:
            reasoning_parts.append("루브릭 기준에 부분적으로 일치")

        return AIGradeResponse(
            answer_id=answer.id,
            question_id=question.id,
            suggested_score=round(suggested_score, 1),
            max_score=float(question.max_score),
            confidence=round(confidence, 2),
            reasoning="; ".join(reasoning_parts),
            matched_keywords=matched_keywords,
            rubric_coverage=round(coverage, 1),
        )

    @staticmethod
    async def calculate_expert_total_score(db: AsyncSession, expert_id: Any) -> ExpertScoreResponse:
        """Calculate and store aggregated scores for an expert.

        Args:
            db: Database session
            expert_id: Expert UUID

        Returns:
            Aggregated score data
        """
        expert_uuid = UUID(str(expert_id)) if not isinstance(expert_id, UUID) else expert_id

        # Get all graded answers with their questions and categories
        result = await db.execute(
            select(Answer, Question, QuestionCategory)
            .join(Question, Answer.question_id == Question.id)
            .join(QuestionCategory, Question.category_id == QuestionCategory.id)
            .where(
                and_(
                    Answer.expert_id == expert_uuid,
                    Answer.status.in_([AnswerStatus.GRADED, AnswerStatus.REVIEWED]),
                )
            )
        )
        rows = result.all()

        # Calculate scores by category
        category_data: dict[str, dict] = {}
        total_score = 0.0
        max_possible_score = 0.0

        for answer, question, category in rows:
            cat_id = str(category.id)
            if cat_id not in category_data:
                category_data[cat_id] = {
                    "category_id": category.id,
                    "category_name": category.name,
                    "score": 0.0,
                    "max_score": 0.0,
                    "graded_count": 0,
                    "total_count": 0,
                }

            category_data[cat_id]["score"] += answer.score or 0.0
            category_data[cat_id]["max_score"] += answer.max_score
            category_data[cat_id]["graded_count"] += 1

            total_score += answer.score or 0.0
            max_possible_score += answer.max_score

        # Get total question count for this expert (including ungraded)
        total_result = await db.execute(
            select(func.count(Answer.id)).where(Answer.expert_id == expert_uuid)
        )
        total_count = total_result.scalar() or 0

        # Calculate percentages
        category_summaries = []
        for cat_id, data in category_data.items():
            percentage = (data["score"] / data["max_score"] * 100) if data["max_score"] > 0 else 0.0
            category_summaries.append(
                CategoryScoreSummary(
                    category_id=data["category_id"],
                    category_name=data["category_name"],
                    score=data["score"],
                    max_score=data["max_score"],
                    percentage=round(percentage, 1),
                    graded_count=data["graded_count"],
                    total_count=data["graded_count"],  # Update later if needed
                )
            )

        average_percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0.0

        # Upsert ExpertScore record
        score_result = await db.execute(
            select(ExpertScore).where(ExpertScore.expert_id == expert_uuid)
        )
        expert_score = score_result.scalar_one_or_none()

        if expert_score:
            expert_score.total_score = total_score
            expert_score.max_possible_score = max_possible_score
            expert_score.average_percentage = round(average_percentage, 1)
            expert_score.category_scores = {
                str(cs.category_id): {
                    "score": cs.score,
                    "max_score": cs.max_score,
                    "percentage": cs.percentage,
                    "graded_count": cs.graded_count,
                }
                for cs in category_summaries
            }
            expert_score.graded_count = len(rows)
            expert_score.total_count = total_count
            expert_score.last_calculated_at = datetime.utcnow()
        else:
            expert_score = ExpertScore(
                expert_id=expert_uuid,
                total_score=total_score,
                max_possible_score=max_possible_score,
                average_percentage=round(average_percentage, 1),
                category_scores={
                    str(cs.category_id): {
                        "score": cs.score,
                        "max_score": cs.max_score,
                        "percentage": cs.percentage,
                        "graded_count": cs.graded_count,
                    }
                    for cs in category_summaries
                },
                graded_count=len(rows),
                total_count=total_count,
                last_calculated_at=datetime.utcnow(),
            )
            db.add(expert_score)

        await db.commit()
        await db.refresh(expert_score)

        return ExpertScoreResponse(
            id=expert_score.id,
            expert_id=expert_score.expert_id,
            total_score=expert_score.total_score,
            max_possible_score=expert_score.max_possible_score,
            average_percentage=expert_score.average_percentage,
            category_scores=category_summaries,
            graded_count=expert_score.graded_count,
            total_count=expert_score.total_count,
            rank=expert_score.rank,
            percentile=expert_score.percentile,
            last_calculated_at=expert_score.last_calculated_at,
        )

    @staticmethod
    async def get_grading_statistics(db: AsyncSession) -> GradingStatistics:
        """Get overall grading statistics for dashboard.

        Args:
            db: Database session

        Returns:
            Grading statistics
        """
        # Expert counts
        total_experts_result = await db.execute(select(func.count(Expert.id)))
        total_experts = total_experts_result.scalar() or 0

        experts_with_submissions_result = await db.execute(
            select(func.count(func.distinct(Answer.expert_id))).where(
                Answer.status != AnswerStatus.DRAFT
            )
        )
        experts_with_submissions = experts_with_submissions_result.scalar() or 0

        # Answer counts
        total_answers_result = await db.execute(
            select(func.count(Answer.id)).where(Answer.status != AnswerStatus.DRAFT)
        )
        total_answers = total_answers_result.scalar() or 0

        graded_answers_result = await db.execute(
            select(func.count(Answer.id)).where(
                Answer.status.in_([AnswerStatus.GRADED, AnswerStatus.REVIEWED])
            )
        )
        graded_answers = graded_answers_result.scalar() or 0

        pending_answers = total_answers - graded_answers

        # Score statistics
        score_stats_result = await db.execute(
            select(
                func.avg(Answer.score),
                func.max(Answer.score),
                func.min(Answer.score),
            ).where(Answer.score.isnot(None))
        )
        score_stats = score_stats_result.one()
        avg_score = float(score_stats[0] or 0)
        max_score = float(score_stats[1] or 0)
        min_score = float(score_stats[2] or 0)

        # Graded today
        today = date.today()
        graded_today_result = await db.execute(
            select(func.count(Answer.id)).where(
                and_(
                    Answer.status.in_([AnswerStatus.GRADED, AnswerStatus.REVIEWED]),
                    func.date(Answer.updated_at) == today,
                )
            )
        )
        graded_today = graded_today_result.scalar() or 0

        # Fully graded experts (all their answers are graded)
        # This is a more complex query
        fully_graded_result = await db.execute(
            select(func.count(func.distinct(Answer.expert_id))).where(
                Answer.status.in_([AnswerStatus.GRADED, AnswerStatus.REVIEWED])
            )
        )
        fully_graded_experts = fully_graded_result.scalar() or 0

        # Category stats
        category_stats_result = await db.execute(
            select(
                QuestionCategory.id,
                QuestionCategory.name,
                func.count(Answer.id).label("answer_count"),
                func.sum(Answer.score).label("total_score"),
            )
            .join(Question, QuestionCategory.id == Question.category_id)
            .join(Answer, Question.id == Answer.question_id)
            .where(Answer.status.in_([AnswerStatus.GRADED, AnswerStatus.REVIEWED]))
            .group_by(QuestionCategory.id, QuestionCategory.name)
        )
        category_stats = [
            {
                "category_id": str(row.id),
                "category_name": row.name,
                "answer_count": row.answer_count,
                "total_score": float(row.total_score or 0),
            }
            for row in category_stats_result.all()
        ]

        return GradingStatistics(
            total_experts=total_experts,
            experts_with_submissions=experts_with_submissions,
            fully_graded_experts=fully_graded_experts,
            total_answers=total_answers,
            graded_answers=graded_answers,
            pending_answers=pending_answers,
            average_score=round(avg_score, 1),
            highest_score=round(max_score, 1),
            lowest_score=round(min_score, 1),
            graded_today=graded_today,
            category_stats=category_stats,
        )

    @staticmethod
    async def get_grading_progress(db: AsyncSession, expert_id: Any) -> GradingProgress:
        """Get grading progress for an expert.

        Args:
            db: Database session
            expert_id: Expert UUID

        Returns:
            Grading progress data
        """
        expert_uuid = UUID(str(expert_id)) if not isinstance(expert_id, UUID) else expert_id

        # Get counts by status
        result = await db.execute(
            select(Answer.status, func.count(Answer.id))
            .where(Answer.expert_id == expert_uuid)
            .group_by(Answer.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}

        draft_count = status_counts.get(AnswerStatus.DRAFT, 0)
        submitted_count = status_counts.get(AnswerStatus.SUBMITTED, 0)
        graded_count = status_counts.get(AnswerStatus.GRADED, 0)
        reviewed_count = status_counts.get(AnswerStatus.REVIEWED, 0)

        total_answers = sum(status_counts.values())
        graded_answers = graded_count + reviewed_count
        pending_answers = submitted_count

        progress_percentage = (graded_answers / total_answers * 100) if total_answers > 0 else 0.0

        return GradingProgress(
            total_answers=total_answers,
            graded_answers=graded_answers,
            pending_answers=pending_answers,
            progress_percentage=round(progress_percentage, 1),
            draft_count=draft_count,
            submitted_count=submitted_count,
            graded_count=graded_count,
            reviewed_count=reviewed_count,
        )
