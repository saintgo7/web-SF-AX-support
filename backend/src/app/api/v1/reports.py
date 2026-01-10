"""Report generation API endpoints."""
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.app.api.deps import get_current_operator, get_db
from src.app.models.user import User
from src.app.models.expert import Expert, QualificationStatus
from src.app.models.question import Question
from src.app.models.answer import Answer, AnswerStatus
from src.app.models.application import Application, ApplicationStatus
from src.app.models.company import Company, Demand, DemandStatus
from src.app.models.matching import Matching, MatchingStatus
from src.app.models.report import Report, ReportType, ReportStatus
from src.app.models.expert_score import ExpertScore
from src.app.schemas.report import (
    ReportResponse as ReportSchemaResponse,
    ReportListResponse,
    GenerateExpertReportRequest,
    GenerateSummaryReportRequest,
    GenerateReportResponse,
    ExpertReportData,
    ExpertReportScoreSummary,
    ExpertReportCategoryScore,
    ExpertReportAnswerDetail,
    SystemReportData,
    SystemReportCategorySummary,
    SystemReportScoreDistribution,
)
from src.app.services.pdf_service import PDFService

router = APIRouter(prefix="/reports", tags=["Reports"])


class SummaryStats(BaseModel):
    """Overall system summary statistics."""

    total_experts: int = 0
    qualified_experts: int = 0
    pending_experts: int = 0
    total_questions: int = 0
    total_answers: int = 0
    graded_answers: int = 0
    pending_grading: int = 0
    average_score: float = 0.0
    completion_rate: float = 0.0
    total_companies: int = 0
    total_demands: int = 0
    total_matchings: int = 0
    active_matchings: int = 0


class ExpertsReport(BaseModel):
    """Expert statistics report."""

    total: int = 0
    by_qualification: dict = {}
    by_specialty: dict = {}
    by_education: dict = {}
    recent_registrations: int = 0
    avg_career_years: float = 0.0


class EvaluationsReport(BaseModel):
    """Evaluation statistics report."""

    total_graded: int = 0
    avg_score: float = 0.0
    score_distribution: dict = {}
    by_question_type: dict = {}
    pass_rate: float = 0.0
    pending_count: int = 0


class MatchingsReport(BaseModel):
    """Matching efficiency report."""

    total: int = 0
    by_status: dict = {}
    by_type: dict = {}
    success_rate: float = 0.0
    avg_match_score: float = 0.0
    monthly_trend: list = []


class ReportResponse(BaseModel):
    """Generic report response."""

    report_type: str
    generated_at: str
    data: dict


@router.get("/summary", response_model=SummaryStats)
async def get_summary_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get overall system summary statistics.

    Args:
        db: Database session
        current_user: Current operator

    Returns:
        System summary statistics
    """
    # Expert counts
    total_experts = (await db.execute(select(func.count()).select_from(Expert))).scalar() or 0
    qualified_experts = (
        await db.execute(
            select(func.count())
            .select_from(Expert)
            .where(Expert.qualification_status == QualificationStatus.QUALIFIED)
        )
    ).scalar() or 0
    pending_experts = (
        await db.execute(
            select(func.count())
            .select_from(Expert)
            .where(Expert.qualification_status == QualificationStatus.PENDING)
        )
    ).scalar() or 0

    # Question and answer counts
    total_questions = (
        await db.execute(select(func.count()).select_from(Question).where(Question.is_active == True))
    ).scalar() or 0

    total_answers = (await db.execute(select(func.count()).select_from(Answer))).scalar() or 0

    graded_answers = (
        await db.execute(
            select(func.count()).select_from(Answer).where(Answer.status == AnswerStatus.GRADED)
        )
    ).scalar() or 0

    pending_grading = (
        await db.execute(
            select(func.count()).select_from(Answer).where(Answer.status == AnswerStatus.SUBMITTED)
        )
    ).scalar() or 0

    # Average score
    avg_score_result = await db.execute(
        select(func.avg(Answer.score)).where(Answer.score.isnot(None))
    )
    average_score = avg_score_result.scalar() or 0.0

    # Completion rate
    completion_rate = (graded_answers / total_answers * 100) if total_answers > 0 else 0.0

    # Company and matching counts
    total_companies = (
        await db.execute(
            select(func.count()).select_from(Company).where(Company.is_active == True)
        )
    ).scalar() or 0

    total_demands = (
        await db.execute(select(func.count()).select_from(Demand).where(Demand.is_active == True))
    ).scalar() or 0

    total_matchings = (
        await db.execute(select(func.count()).select_from(Matching).where(Matching.is_active == True))
    ).scalar() or 0

    active_matchings = (
        await db.execute(
            select(func.count())
            .select_from(Matching)
            .where(
                Matching.is_active == True,
                Matching.status.in_([MatchingStatus.PROPOSED, MatchingStatus.ACCEPTED, MatchingStatus.IN_PROGRESS]),
            )
        )
    ).scalar() or 0

    return SummaryStats(
        total_experts=total_experts,
        qualified_experts=qualified_experts,
        pending_experts=pending_experts,
        total_questions=total_questions,
        total_answers=total_answers,
        graded_answers=graded_answers,
        pending_grading=pending_grading,
        average_score=round(float(average_score), 2),
        completion_rate=round(completion_rate, 1),
        total_companies=total_companies,
        total_demands=total_demands,
        total_matchings=total_matchings,
        active_matchings=active_matchings,
    )


@router.get("/experts", response_model=ExpertsReport)
async def get_experts_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get expert statistics report.

    Args:
        db: Database session
        current_user: Current operator

    Returns:
        Expert statistics
    """
    total = (await db.execute(select(func.count()).select_from(Expert))).scalar() or 0

    # By qualification status
    by_qualification = {}
    for status in QualificationStatus:
        count = (
            await db.execute(
                select(func.count())
                .select_from(Expert)
                .where(Expert.qualification_status == status)
            )
        ).scalar() or 0
        by_qualification[status.value] = count

    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = (
        await db.execute(
            select(func.count())
            .select_from(Expert)
            .where(Expert.created_at >= thirty_days_ago)
        )
    ).scalar() or 0

    # Average career years
    avg_career_result = await db.execute(
        select(func.avg(Expert.career_years)).where(Expert.career_years.isnot(None))
    )
    avg_career_years = avg_career_result.scalar() or 0.0

    return ExpertsReport(
        total=total,
        by_qualification=by_qualification,
        by_specialty={},  # Would need to aggregate JSON field
        by_education={},  # Would need to aggregate JSON field
        recent_registrations=recent_registrations,
        avg_career_years=round(float(avg_career_years), 1),
    )


@router.get("/evaluations", response_model=EvaluationsReport)
async def get_evaluations_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get evaluation statistics report.

    Args:
        db: Database session
        current_user: Current operator

    Returns:
        Evaluation statistics
    """
    # Graded answers
    total_graded = (
        await db.execute(
            select(func.count()).select_from(Answer).where(Answer.status == AnswerStatus.GRADED)
        )
    ).scalar() or 0

    # Average score
    avg_result = await db.execute(
        select(func.avg(Answer.score)).where(Answer.score.isnot(None))
    )
    avg_score = avg_result.scalar() or 0.0

    # Pending count
    pending_count = (
        await db.execute(
            select(func.count()).select_from(Answer).where(Answer.status == AnswerStatus.SUBMITTED)
        )
    ).scalar() or 0

    # Score distribution
    score_distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}

    scores_result = await db.execute(
        select(Answer.score, Answer.max_score).where(Answer.score.isnot(None))
    )
    for score, max_score in scores_result:
        if max_score and max_score > 0:
            percentage = (score / max_score) * 100
            if percentage <= 20:
                score_distribution["0-20"] += 1
            elif percentage <= 40:
                score_distribution["21-40"] += 1
            elif percentage <= 60:
                score_distribution["41-60"] += 1
            elif percentage <= 80:
                score_distribution["61-80"] += 1
            else:
                score_distribution["81-100"] += 1

    # Pass rate (assuming 60% is pass)
    passing_count = score_distribution["61-80"] + score_distribution["81-100"]
    pass_rate = (passing_count / total_graded * 100) if total_graded > 0 else 0.0

    return EvaluationsReport(
        total_graded=total_graded,
        avg_score=round(float(avg_score), 2),
        score_distribution=score_distribution,
        by_question_type={},  # Would need to join with Question
        pass_rate=round(pass_rate, 1),
        pending_count=pending_count,
    )


@router.get("/matchings", response_model=MatchingsReport)
async def get_matchings_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Get matching efficiency report.

    Args:
        db: Database session
        current_user: Current operator

    Returns:
        Matching statistics
    """
    total = (
        await db.execute(select(func.count()).select_from(Matching).where(Matching.is_active == True))
    ).scalar() or 0

    # By status
    by_status = {}
    for status in MatchingStatus:
        count = (
            await db.execute(
                select(func.count())
                .select_from(Matching)
                .where(Matching.status == status, Matching.is_active == True)
            )
        ).scalar() or 0
        by_status[status.value] = count

    # By type
    by_type = {"AUTO": 0, "MANUAL": 0}
    for m_type in ["AUTO", "MANUAL"]:
        count = (
            await db.execute(
                select(func.count())
                .select_from(Matching)
                .where(Matching.matching_type == m_type, Matching.is_active == True)
            )
        ).scalar() or 0
        by_type[m_type] = count

    # Success rate (completed / (completed + rejected + cancelled))
    completed = by_status.get("COMPLETED", 0)
    rejected = by_status.get("REJECTED", 0)
    cancelled = by_status.get("CANCELLED", 0)
    total_resolved = completed + rejected + cancelled
    success_rate = (completed / total_resolved * 100) if total_resolved > 0 else 0.0

    # Average match score
    avg_score_result = await db.execute(
        select(func.avg(Matching.match_score)).where(
            Matching.match_score.isnot(None), Matching.is_active == True
        )
    )
    avg_match_score = avg_score_result.scalar() or 0.0

    return MatchingsReport(
        total=total,
        by_status=by_status,
        by_type=by_type,
        success_rate=round(success_rate, 1),
        avg_match_score=round(float(avg_match_score), 1),
        monthly_trend=[],  # Would need date grouping
    )


@router.get("/generate/{report_type}", response_model=ReportResponse)
async def generate_report(
    report_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Generate a specific type of report.

    Args:
        report_type: Type of report (summary, experts, evaluations, matchings)
        db: Database session
        current_user: Current operator

    Returns:
        Generated report data
    """
    data = {}

    if report_type == "summary":
        stats = await get_summary_stats(db=db, current_user=current_user)
        data = stats.model_dump()
    elif report_type == "experts":
        report = await get_experts_report(db=db, current_user=current_user)
        data = report.model_dump()
    elif report_type == "evaluations":
        report = await get_evaluations_report(db=db, current_user=current_user)
        data = report.model_dump()
    elif report_type == "matchings":
        report = await get_matchings_report(db=db, current_user=current_user)
        data = report.model_dump()
    else:
        data = {"error": f"Unknown report type: {report_type}"}

    return ReportResponse(
        report_type=report_type,
        generated_at=datetime.utcnow().isoformat(),
        data=data,
    )


# PDF Generation Endpoints
@router.post("/generate/expert/{expert_id}", response_model=GenerateReportResponse)
async def generate_expert_pdf_report(
    expert_id: UUID,
    include_answers: bool = Query(default=True, description="Include detailed answers"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Generate a PDF report for a specific expert.

    Args:
        expert_id: Expert UUID
        include_answers: Whether to include detailed answer breakdown
        db: Database session
        current_user: Current operator

    Returns:
        Report generation response with report ID
    """
    from src.app.models.question import QuestionCategory

    # Verify expert exists and get expert info
    expert_result = await db.execute(
        select(Expert).where(Expert.id == expert_id)
    )
    expert = expert_result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found",
        )

    # Get expert's user info
    user_result = await db.execute(
        select(User).where(User.id == expert.user_id)
    )
    expert_user = user_result.scalar_one_or_none()

    # Get expert score
    score_result = await db.execute(
        select(ExpertScore).where(ExpertScore.expert_id == expert_id)
    )
    expert_score = score_result.scalar_one_or_none()

    # Build score summary
    if expert_score:
        score_summary = ExpertReportScoreSummary(
            total_score=expert_score.total_score,
            max_possible_score=expert_score.max_possible_score,
            percentage=expert_score.average_percentage,
            rank=expert_score.rank,
            percentile=expert_score.percentile,
        )
    else:
        score_summary = ExpertReportScoreSummary(
            total_score=0, max_possible_score=0, percentage=0
        )

    # Build category scores
    category_scores = []
    if expert_score and expert_score.category_scores:
        for cat_id, cat_data in expert_score.category_scores.items():
            category_scores.append(
                ExpertReportCategoryScore(
                    category_id=cat_id,
                    category_name=cat_data.get("category_name", "Unknown"),
                    score=cat_data.get("score", 0),
                    max_score=cat_data.get("max_score", 0),
                    percentage=cat_data.get("percentage", 0),
                    question_count=cat_data.get("total_count", 0),
                    answered_count=cat_data.get("graded_count", 0),
                )
            )

    # Get answer details if requested
    answer_details = []
    if include_answers:
        answers_result = await db.execute(
            select(Answer, Question)
            .join(Question, Answer.question_id == Question.id)
            .where(Answer.expert_id == expert_id)
            .order_by(Answer.created_at)
        )
        for answer, question in answers_result:
            # Get category name
            cat_result = await db.execute(
                select(QuestionCategory).where(QuestionCategory.id == question.category_id)
            )
            category = cat_result.scalar_one_or_none()

            answer_details.append(
                ExpertReportAnswerDetail(
                    question_id=str(question.id),
                    question_content=question.content,
                    question_type=question.q_type.value if hasattr(question.q_type, 'value') else str(question.q_type),
                    category_name=category.name if category else "Unknown",
                    response_summary=str(answer.response_data)[:200] if answer.response_data else "",
                    score=answer.score,
                    max_score=question.max_score,
                    grader_comment=answer.grader_comment,
                )
            )

    # Create report data
    report_data = ExpertReportData(
        expert_id=str(expert_id),
        expert_name=expert_user.name if expert_user else "Unknown",
        email=expert_user.email if expert_user else "",
        phone=expert_user.phone if expert_user else None,
        specialty=",".join(expert.specialties) if expert.specialties else None,
        organization=expert.current_org if expert.current_org else None,
        score_summary=score_summary,
        category_scores=category_scores,
        answer_details=answer_details,
        generated_at=datetime.utcnow(),
    )

    # Create report record
    report = Report(
        report_type=ReportType.EXPERT_EVALUATION,
        title=f"전문가 평가 보고서 - {expert_user.name if expert_user else 'Unknown'}",
        parameters={"expert_id": str(expert_id), "include_answers": include_answers},
        data=report_data.model_dump(mode="json"),
        status=ReportStatus.PROCESSING,
        generated_by=current_user.id,
        expert_id=expert_id,
        started_at=datetime.utcnow(),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Generate PDF
    try:
        pdf_content = await PDFService.generate_expert_report(report_data)

        # Save file
        filename = f"expert_report_{expert_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = await PDFService.save_report_file(pdf_content, filename)

        # Update report record
        report.file_url = file_path
        report.file_size = len(pdf_content)
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.utcnow()
        await db.commit()

    except Exception as e:
        report.status = ReportStatus.FAILED
        report.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}",
        )

    return GenerateReportResponse(
        report_id=report.id,
        status=report.status,
        message=f"Report generated successfully for expert {expert_user.name if expert_user else 'Unknown'}",
    )


@router.post("/generate/summary", response_model=GenerateReportResponse)
async def generate_summary_pdf_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Generate a system summary PDF report.

    Args:
        db: Database session
        current_user: Current operator

    Returns:
        Report generation response with report ID
    """
    from src.app.models.question import QuestionCategory

    # Get statistics
    stats = await get_summary_stats(db=db, current_user=current_user)

    # Get category summaries
    categories_result = await db.execute(
        select(QuestionCategory).where(QuestionCategory.is_active == True)
    )
    categories = list(categories_result.scalars().all())

    category_summaries = []
    for cat in categories:
        # Count questions in category
        q_count = (
            await db.execute(
                select(func.count())
                .select_from(Question)
                .where(Question.category_id == cat.id, Question.is_active == True)
            )
        ).scalar() or 0

        # Count answers for questions in this category
        a_count = (
            await db.execute(
                select(func.count())
                .select_from(Answer)
                .join(Question, Answer.question_id == Question.id)
                .where(Question.category_id == cat.id)
            )
        ).scalar() or 0

        # Count graded answers
        graded_count = (
            await db.execute(
                select(func.count())
                .select_from(Answer)
                .join(Question, Answer.question_id == Question.id)
                .where(Question.category_id == cat.id, Answer.status == AnswerStatus.GRADED)
            )
        ).scalar() or 0

        # Average score for category
        avg_result = await db.execute(
            select(func.avg(Answer.score / Answer.max_score * 100))
            .join(Question, Answer.question_id == Question.id)
            .where(
                Question.category_id == cat.id,
                Answer.score.isnot(None),
                Answer.max_score > 0,
            )
        )
        avg_score = avg_result.scalar() or 0.0

        # Min/max scores
        min_result = await db.execute(
            select(func.min(Answer.score / Answer.max_score * 100))
            .join(Question, Answer.question_id == Question.id)
            .where(
                Question.category_id == cat.id,
                Answer.score.isnot(None),
                Answer.max_score > 0,
            )
        )
        min_score = min_result.scalar() or 0.0

        max_result = await db.execute(
            select(func.max(Answer.score / Answer.max_score * 100))
            .join(Question, Answer.question_id == Question.id)
            .where(
                Question.category_id == cat.id,
                Answer.score.isnot(None),
                Answer.max_score > 0,
            )
        )
        max_score = max_result.scalar() or 0.0

        category_summaries.append(
            SystemReportCategorySummary(
                category_id=str(cat.id),
                category_name=cat.name,
                total_questions=q_count,
                total_answers=a_count,
                graded_answers=graded_count,
                average_score=float(avg_score),
                highest_score=float(max_score),
                lowest_score=float(min_score),
            )
        )

    # Score distribution
    score_distribution = []
    ranges = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
    total_graded = stats.graded_answers

    for start, end in ranges:
        count = (
            await db.execute(
                select(func.count())
                .select_from(Answer)
                .where(
                    Answer.score.isnot(None),
                    Answer.max_score > 0,
                    (Answer.score / Answer.max_score * 100) >= start,
                    (Answer.score / Answer.max_score * 100) < end if end < 100 else True,
                )
            )
        ).scalar() or 0

        score_distribution.append(
            SystemReportScoreDistribution(
                range_start=float(start),
                range_end=float(end),
                count=count,
                percentage=(count / total_graded * 100) if total_graded > 0 else 0,
            )
        )

    # Create report data
    report_data = SystemReportData(
        total_experts=stats.total_experts,
        experts_with_submissions=stats.total_experts - stats.pending_experts,
        fully_graded_experts=stats.qualified_experts,
        average_expert_score=stats.average_score,
        total_questions=stats.total_questions,
        total_answers=stats.total_answers,
        graded_answers=stats.graded_answers,
        pending_answers=stats.pending_grading,
        category_summaries=category_summaries,
        score_distribution=score_distribution,
        generated_at=datetime.utcnow(),
    )

    # Create report record
    report = Report(
        report_type=ReportType.SYSTEM_SUMMARY,
        title=f"시스템 종합 보고서 - {datetime.utcnow().strftime('%Y년 %m월 %d일')}",
        parameters={},
        data=report_data.model_dump(mode="json"),
        status=ReportStatus.PROCESSING,
        generated_by=current_user.id,
        started_at=datetime.utcnow(),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Generate PDF
    try:
        pdf_content = await PDFService.generate_summary_report(report_data)

        # Save file
        filename = f"system_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = await PDFService.save_report_file(pdf_content, filename)

        # Update report record
        report.file_url = file_path
        report.file_size = len(pdf_content)
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.utcnow()
        await db.commit()

    except Exception as e:
        report.status = ReportStatus.FAILED
        report.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}",
        )

    return GenerateReportResponse(
        report_id=report.id,
        status=report.status,
        message="System summary report generated successfully",
    )


@router.get("/download/{report_id}")
async def download_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """Download a generated report PDF.

    Args:
        report_id: Report UUID
        db: Database session
        current_user: Current operator

    Returns:
        PDF file response
    """
    # Get report
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready. Status: {report.status.value}",
        )

    if not report.file_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report file not found",
        )

    # Read file
    try:
        with open(report.file_url, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on disk",
        )

    # Determine content type
    content_type = "application/pdf" if report.file_url.endswith(".pdf") else "application/octet-stream"
    filename = report.file_url.split("/")[-1]

    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/list", response_model=ReportListResponse)
async def list_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    report_type: ReportType | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
):
    """List generated reports with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        report_type: Filter by report type
        db: Database session
        current_user: Current operator

    Returns:
        Paginated list of reports
    """
    query = select(Report).order_by(Report.created_at.desc())

    if report_type:
        query = query.where(Report.report_type == report_type)

    # Count total
    count_query = select(func.count()).select_from(Report)
    if report_type:
        count_query = count_query.where(Report.report_type == report_type)
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated results
    result = await db.execute(query.offset(skip).limit(limit))
    reports = list(result.scalars().all())

    return ReportListResponse(
        items=[ReportSchemaResponse.model_validate(r) for r in reports],
        total=total,
        skip=skip,
        limit=limit,
    )
