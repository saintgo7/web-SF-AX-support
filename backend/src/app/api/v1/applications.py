"""Application management API endpoints."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_active_user, get_current_operator, get_db
from src.app.models.user import User
from src.app.models.application import Application, ApplicationStatus, ApplicationType
from src.app.models.expert import Expert
from src.app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationSubmit,
    ApplicationReview,
    Application as ApplicationSchema,
    ApplicationList,
    ApplicationSummary,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationSchema, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Application:
    """Create a new application.

    Args:
        application_data: Application creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created application
    """
    # Verify expert exists and belongs to current user
    result = await db.execute(
        select(Expert).where(Expert.id == application_data.expert_id)
    )
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    if expert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create applications for your own expert profile",
        )

    # Create application
    application = Application(
        expert_id=application_data.expert_id,
        application_type=application_data.application_type,
        title=application_data.title,
        description=application_data.description,
        documents=application_data.documents,
        form_data=application_data.form_data,
        status=ApplicationStatus.DRAFT,
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return application


@router.get("", response_model=ApplicationList)
async def get_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: ApplicationStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationList:
    """Get applications for the current user.

    Args:
        page: Page number
        page_size: Items per page
        status_filter: Optional status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of applications
    """
    # Get expert for current user
    result = await db.execute(
        select(Expert).where(Expert.user_id == current_user.id)
    )
    expert = result.scalar_one_or_none()

    if not expert:
        return ApplicationList(items=[], total=0, page=page, page_size=page_size)

    # Build query
    query = select(Application).where(Application.expert_id == expert.id)
    count_query = select(func.count()).select_from(Application).where(Application.expert_id == expert.id)

    if status_filter:
        query = query.where(Application.status == status_filter)
        count_query = count_query.where(Application.status == status_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Application.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    applications = result.scalars().all()

    return ApplicationList(
        items=list(applications),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/summary", response_model=ApplicationSummary)
async def get_application_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationSummary:
    """Get application summary statistics for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Application summary statistics
    """
    # Get expert for current user
    result = await db.execute(
        select(Expert).where(Expert.user_id == current_user.id)
    )
    expert = result.scalar_one_or_none()

    if not expert:
        return ApplicationSummary()

    # Get counts by status
    result = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.expert_id == expert.id)
        .group_by(Application.status)
    )
    status_counts = dict(result.all())

    return ApplicationSummary(
        total=sum(status_counts.values()),
        draft=status_counts.get(ApplicationStatus.DRAFT, 0),
        submitted=status_counts.get(ApplicationStatus.SUBMITTED, 0),
        under_review=status_counts.get(ApplicationStatus.UNDER_REVIEW, 0),
        approved=status_counts.get(ApplicationStatus.APPROVED, 0),
        rejected=status_counts.get(ApplicationStatus.REJECTED, 0),
    )


@router.get("/all", response_model=ApplicationList)
async def get_all_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: ApplicationStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> ApplicationList:
    """Get all applications (admin/operator only).

    Args:
        page: Page number
        page_size: Items per page
        status_filter: Optional status filter
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Paginated list of all applications
    """
    # Build query
    query = select(Application)
    count_query = select(func.count()).select_from(Application)

    if status_filter:
        query = query.where(Application.status == status_filter)
        count_query = count_query.where(Application.status == status_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Application.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    applications = result.scalars().all()

    return ApplicationList(
        items=list(applications),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{application_id}", response_model=ApplicationSchema)
async def get_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Application:
    """Get a specific application.

    Args:
        application_id: Application ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Application details
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Check access rights
    expert_result = await db.execute(
        select(Expert).where(Expert.id == application.expert_id)
    )
    expert = expert_result.scalar_one_or_none()

    if expert and expert.user_id != current_user.id:
        # Check if user is operator/admin
        if current_user.role.value not in ["OPERATOR", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this application",
            )

    return application


@router.put("/{application_id}", response_model=ApplicationSchema)
async def update_application(
    application_id: UUID,
    update_data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Application:
    """Update an application (only DRAFT status).

    Args:
        application_id: Application ID
        update_data: Update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated application
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Verify ownership
    expert_result = await db.execute(
        select(Expert).where(Expert.id == application.expert_id)
    )
    expert = expert_result.scalar_one_or_none()

    if not expert or expert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own applications",
        )

    # Only allow updates for DRAFT status
    if application.status != ApplicationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update applications in DRAFT status",
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(application, field, value)

    await db.commit()
    await db.refresh(application)

    return application


@router.post("/{application_id}/submit", response_model=ApplicationSchema)
async def submit_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Application:
    """Submit an application for review.

    Args:
        application_id: Application ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Submitted application
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Verify ownership
    expert_result = await db.execute(
        select(Expert).where(Expert.id == application.expert_id)
    )
    expert = expert_result.scalar_one_or_none()

    if not expert or expert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own applications",
        )

    # Only allow submission of DRAFT applications
    if application.status != ApplicationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only submit applications in DRAFT status",
        )

    # Update status
    application.status = ApplicationStatus.SUBMITTED

    await db.commit()
    await db.refresh(application)

    return application


@router.post("/{application_id}/review", response_model=ApplicationSchema)
async def review_application(
    application_id: UUID,
    review_data: ApplicationReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Application:
    """Review an application (approve/reject).

    Args:
        application_id: Application ID
        review_data: Review decision
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Reviewed application
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Only allow review of SUBMITTED or UNDER_REVIEW applications
    if application.status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review submitted applications",
        )

    # Validate new status
    if review_data.status not in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review status must be APPROVED or REJECTED",
        )

    # Update application
    application.status = review_data.status
    application.reviewer_id = current_user.id
    application.review_note = review_data.review_note
    application.reviewed_at = datetime.utcnow().isoformat()

    await db.commit()
    await db.refresh(application)

    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete an application (only DRAFT status).

    Args:
        application_id: Application ID
        db: Database session
        current_user: Current authenticated user
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Verify ownership
    expert_result = await db.execute(
        select(Expert).where(Expert.id == application.expert_id)
    )
    expert = expert_result.scalar_one_or_none()

    if not expert or expert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own applications",
        )

    # Only allow deletion of DRAFT applications
    if application.status != ApplicationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete applications in DRAFT status",
        )

    await db.delete(application)
    await db.commit()
