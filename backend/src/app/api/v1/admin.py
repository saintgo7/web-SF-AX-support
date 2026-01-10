"""Admin API endpoints for dashboard statistics and management."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.app.api.deps import get_current_operator, get_db
from src.app.models.user import User
from src.app.models.expert import Expert, QualificationStatus
from src.app.models.application import Application, ApplicationStatus
from src.app.models.company import Company, Demand, DemandStatus
from src.app.models.matching import Matching, MatchingStatus
from src.app.models.answer import Answer, AnswerStatus

router = APIRouter(prefix="/admin", tags=["Admin"])


class DashboardStats(BaseModel):
    """Dashboard statistics response schema."""

    total_experts: int = 0
    qualified_experts: int = 0
    pending_applications: int = 0
    active_evaluations: int = 0
    completed_matchings: int = 0
    total_companies: int = 0
    pending_demands: int = 0


class RecentActivity(BaseModel):
    """Recent activity item schema."""

    type: str
    message: str
    timestamp: str


class DashboardResponse(BaseModel):
    """Dashboard response schema."""

    stats: DashboardStats
    recent_activities: list[RecentActivity]


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> DashboardStats:
    """Get dashboard statistics for admin panel.

    Args:
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Dashboard statistics
    """
    # Total experts
    total_experts_result = await db.execute(select(func.count()).select_from(Expert))
    total_experts = total_experts_result.scalar() or 0

    # Qualified experts
    qualified_experts_result = await db.execute(
        select(func.count())
        .select_from(Expert)
        .where(Expert.qualification_status == QualificationStatus.QUALIFIED)
    )
    qualified_experts = qualified_experts_result.scalar() or 0

    # Pending applications (SUBMITTED status)
    pending_apps_result = await db.execute(
        select(func.count())
        .select_from(Application)
        .where(Application.status == ApplicationStatus.SUBMITTED)
    )
    pending_applications = pending_apps_result.scalar() or 0

    # Active evaluations (answers in SUBMITTED status waiting for grading)
    active_evals_result = await db.execute(
        select(func.count(func.distinct(Answer.expert_id)))
        .select_from(Answer)
        .where(Answer.status == AnswerStatus.SUBMITTED)
    )
    active_evaluations = active_evals_result.scalar() or 0

    # Completed matchings
    completed_matchings_result = await db.execute(
        select(func.count())
        .select_from(Matching)
        .where(Matching.status == MatchingStatus.COMPLETED)
    )
    completed_matchings = completed_matchings_result.scalar() or 0

    # Total companies
    total_companies_result = await db.execute(
        select(func.count())
        .select_from(Company)
        .where(Company.is_active == True)
    )
    total_companies = total_companies_result.scalar() or 0

    # Pending demands
    pending_demands_result = await db.execute(
        select(func.count())
        .select_from(Demand)
        .where(Demand.status == DemandStatus.PENDING, Demand.is_active == True)
    )
    pending_demands = pending_demands_result.scalar() or 0

    return DashboardStats(
        total_experts=total_experts,
        qualified_experts=qualified_experts,
        pending_applications=pending_applications,
        active_evaluations=active_evaluations,
        completed_matchings=completed_matchings,
        total_companies=total_companies,
        pending_demands=pending_demands,
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> DashboardResponse:
    """Get full dashboard data including stats and recent activities.

    Args:
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Dashboard data with stats and recent activities
    """
    stats = await get_dashboard_stats(db=db, current_user=current_user)

    # Get recent activities (simplified - in production, you'd query from an activity log)
    recent_activities = []

    # Recent applications
    recent_apps = await db.execute(
        select(Application)
        .order_by(Application.created_at.desc())
        .limit(3)
    )
    for app in recent_apps.scalars():
        recent_activities.append(RecentActivity(
            type="application",
            message=f"새 신청서: {app.title}",
            timestamp=app.created_at.isoformat(),
        ))

    # Recent matchings
    recent_matchings = await db.execute(
        select(Matching)
        .order_by(Matching.created_at.desc())
        .limit(2)
    )
    for matching in recent_matchings.scalars():
        recent_activities.append(RecentActivity(
            type="matching",
            message=f"매칭 상태 변경: {matching.status.value if hasattr(matching.status, 'value') else matching.status}",
            timestamp=matching.created_at.isoformat(),
        ))

    # Sort by timestamp
    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activities = recent_activities[:5]

    return DashboardResponse(
        stats=stats,
        recent_activities=recent_activities,
    )
