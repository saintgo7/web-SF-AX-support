"""Matching management API endpoints."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_active_user, get_current_operator, get_db
from src.app.models.user import User
from src.app.models.expert import Expert, QualificationStatus
from src.app.models.company import Demand, DemandStatus
from src.app.models.matching import Matching, MatchingStatus, MatchingType
from src.app.schemas.matching import (
    MatchingCreate,
    MatchingUpdate,
    MatchingExpertResponse,
    MatchingCompanyFeedback,
    Matching as MatchingSchema,
    MatchingWithDetails,
    MatchingList,
    MatchingSummary,
    AutoMatchRequest,
    AutoMatchResponse,
    MatchCandidate,
    # Sprint 6: Enhanced matching
    MatchScoreBreakdown,
    RecommendedCandidate,
    RecommendRequest,
    RecommendResponse,
    CompatibilityCheckResponse,
    MatchingAnalytics,
)
from src.app.services.matching_service import MatchingService

router = APIRouter(prefix="/matchings", tags=["Matchings"])


def calculate_match_score(
    expert: Expert,
    demand: Demand,
) -> tuple[float, dict]:
    """Calculate match score between expert and demand.

    Args:
        expert: Expert model
        demand: Demand model

    Returns:
        Tuple of (score, score_breakdown)
    """
    score_breakdown = {}
    total_score = 0.0
    max_possible = 100.0

    # 1. Specialty match (40 points max)
    specialty_score = 0.0
    if expert.specialties and demand.required_specialties:
        expert_specs = set(expert.specialties) if isinstance(expert.specialties, list) else set()
        required_specs = set(demand.required_specialties) if isinstance(demand.required_specialties, list) else set()

        if required_specs:
            matched = len(expert_specs & required_specs)
            specialty_score = (matched / len(required_specs)) * 40
    score_breakdown["specialty_match"] = {
        "score": specialty_score,
        "max": 40,
        "description": "전문 분야 일치도",
    }
    total_score += specialty_score

    # 2. Qualification status (20 points max)
    qualification_score = 0.0
    if expert.qualification_status == QualificationStatus.QUALIFIED:
        qualification_score = 20.0
    elif expert.qualification_status == QualificationStatus.PENDING:
        qualification_score = 10.0
    score_breakdown["qualification"] = {
        "score": qualification_score,
        "max": 20,
        "description": "자격 검증 상태",
    }
    total_score += qualification_score

    # 3. Career experience (20 points max)
    career_score = 0.0
    if expert.career_years:
        if expert.career_years >= 10:
            career_score = 20.0
        elif expert.career_years >= 7:
            career_score = 15.0
        elif expert.career_years >= 5:
            career_score = 10.0
        elif expert.career_years >= 3:
            career_score = 5.0
    score_breakdown["career_experience"] = {
        "score": career_score,
        "max": 20,
        "description": "경력 연수",
    }
    total_score += career_score

    # 4. Education level (20 points max)
    education_score = 0.0
    if expert.degree_type:
        if expert.degree_type.value == "PHD":
            education_score = 20.0
        elif expert.degree_type.value == "MASTER":
            education_score = 15.0
        elif expert.degree_type.value == "BACHELOR":
            education_score = 10.0
    score_breakdown["education"] = {
        "score": education_score,
        "max": 20,
        "description": "학력",
    }
    total_score += education_score

    return total_score, score_breakdown


@router.post("", response_model=MatchingSchema, status_code=status.HTTP_201_CREATED)
async def create_matching(
    matching_data: MatchingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Matching:
    """Create a manual matching.

    Args:
        matching_data: Matching creation data
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Created matching
    """
    # Verify expert exists
    result = await db.execute(
        select(Expert).where(Expert.id == matching_data.expert_id)
    )
    expert = result.scalar_one_or_none()
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    # Verify demand exists
    result = await db.execute(
        select(Demand).where(Demand.id == matching_data.demand_id)
    )
    demand = result.scalar_one_or_none()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    # Check for existing active matching
    result = await db.execute(
        select(Matching).where(
            and_(
                Matching.expert_id == matching_data.expert_id,
                Matching.demand_id == matching_data.demand_id,
                Matching.is_active == True,
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matching already exists for this expert and demand",
        )

    # Calculate score if not provided
    match_score = matching_data.match_score
    score_breakdown = None
    if match_score is None:
        match_score, score_breakdown = calculate_match_score(expert, demand)

    matching = Matching(
        expert_id=matching_data.expert_id,
        demand_id=matching_data.demand_id,
        matching_type=MatchingType.MANUAL,
        match_score=match_score,
        score_breakdown=score_breakdown,
        matching_reason=matching_data.matching_reason,
        matched_by=current_user.id,
        status=MatchingStatus.PROPOSED,
    )

    db.add(matching)
    await db.commit()
    await db.refresh(matching)

    return matching


@router.post("/auto-match", response_model=AutoMatchResponse)
async def auto_match(
    request: AutoMatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> AutoMatchResponse:
    """Find matching candidates for a demand using auto-matching algorithm.

    Args:
        request: Auto-match request with demand_id
        db: Database session
        current_user: Current operator/admin user

    Returns:
        List of matching candidates with scores
    """
    # Verify demand exists
    result = await db.execute(
        select(Demand).where(Demand.id == request.demand_id)
    )
    demand = result.scalar_one_or_none()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    # Get all qualified experts
    result = await db.execute(
        select(Expert).where(
            Expert.qualification_status.in_([
                QualificationStatus.QUALIFIED,
                QualificationStatus.PENDING,
            ])
        )
    )
    experts = result.scalars().all()

    # Calculate scores for each expert
    candidates = []
    for expert in experts:
        score, breakdown = calculate_match_score(expert, demand)

        if score >= request.min_score:
            # Get user name for display
            from src.app.models.user import User as UserModel
            user_result = await db.execute(
                select(UserModel).where(UserModel.id == expert.user_id)
            )
            user = user_result.scalar_one_or_none()

            candidates.append(MatchCandidate(
                expert_id=expert.id,
                expert_name=user.name if user else "Unknown",
                match_score=score,
                score_breakdown=breakdown,
                specialties=expert.specialties if isinstance(expert.specialties, list) else None,
                qualification_status=expert.qualification_status.value,
            ))

    # Sort by score descending and limit
    candidates.sort(key=lambda x: x.match_score, reverse=True)
    candidates = candidates[:request.max_candidates]

    return AutoMatchResponse(
        demand_id=request.demand_id,
        candidates=candidates,
        total_candidates=len(candidates),
    )


@router.post("/auto-match/{demand_id}/create", response_model=list[MatchingSchema])
async def create_auto_matchings(
    demand_id: UUID,
    expert_ids: list[UUID],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> list[Matching]:
    """Create matchings for selected auto-match candidates.

    Args:
        demand_id: Demand ID
        expert_ids: List of expert IDs to create matchings for
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Created matchings
    """
    # Verify demand exists
    result = await db.execute(
        select(Demand).where(Demand.id == demand_id)
    )
    demand = result.scalar_one_or_none()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    matchings = []
    for expert_id in expert_ids:
        # Verify expert exists
        result = await db.execute(
            select(Expert).where(Expert.id == expert_id)
        )
        expert = result.scalar_one_or_none()
        if not expert:
            continue

        # Check for existing matching
        result = await db.execute(
            select(Matching).where(
                and_(
                    Matching.expert_id == expert_id,
                    Matching.demand_id == demand_id,
                    Matching.is_active == True,
                )
            )
        )
        if result.scalar_one_or_none():
            continue

        # Calculate score
        match_score, score_breakdown = calculate_match_score(expert, demand)

        matching = Matching(
            expert_id=expert_id,
            demand_id=demand_id,
            matching_type=MatchingType.AUTO,
            match_score=match_score,
            score_breakdown=score_breakdown,
            matched_by=current_user.id,
            status=MatchingStatus.PROPOSED,
        )

        db.add(matching)
        matchings.append(matching)

    if matchings:
        # Update demand status
        demand.status = DemandStatus.MATCHED
        await db.commit()
        for matching in matchings:
            await db.refresh(matching)

    return matchings


@router.get("", response_model=MatchingList)
async def get_matchings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: MatchingStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MatchingList:
    """Get matchings.

    Args:
        page: Page number
        page_size: Items per page
        status_filter: Optional status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of matchings
    """
    query = select(Matching).where(Matching.is_active == True)
    count_query = select(func.count()).select_from(Matching).where(Matching.is_active == True)

    if status_filter:
        query = query.where(Matching.status == status_filter)
        count_query = count_query.where(Matching.status == status_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Matching.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    matchings = result.scalars().all()

    return MatchingList(
        items=list(matchings),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/summary", response_model=MatchingSummary)
async def get_matching_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> MatchingSummary:
    """Get matching summary statistics.

    Args:
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Matching summary statistics
    """
    result = await db.execute(
        select(Matching.status, func.count(Matching.id))
        .where(Matching.is_active == True)
        .group_by(Matching.status)
    )
    status_counts = dict(result.all())

    return MatchingSummary(
        total=sum(status_counts.values()),
        proposed=status_counts.get(MatchingStatus.PROPOSED, 0),
        accepted=status_counts.get(MatchingStatus.ACCEPTED, 0),
        rejected=status_counts.get(MatchingStatus.REJECTED, 0),
        in_progress=status_counts.get(MatchingStatus.IN_PROGRESS, 0),
        completed=status_counts.get(MatchingStatus.COMPLETED, 0),
    )


@router.get("/expert/{expert_id}", response_model=MatchingList)
async def get_expert_matchings(
    expert_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MatchingList:
    """Get matchings for a specific expert.

    Args:
        expert_id: Expert ID
        page: Page number
        page_size: Items per page
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of matchings for the expert
    """
    query = select(Matching).where(
        Matching.expert_id == expert_id,
        Matching.is_active == True,
    )
    count_query = select(func.count()).select_from(Matching).where(
        Matching.expert_id == expert_id,
        Matching.is_active == True,
    )

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Matching.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    matchings = result.scalars().all()

    return MatchingList(
        items=list(matchings),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{matching_id}", response_model=MatchingSchema)
async def get_matching(
    matching_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Matching:
    """Get a specific matching.

    Args:
        matching_id: Matching ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Matching details
    """
    result = await db.execute(
        select(Matching).where(Matching.id == matching_id)
    )
    matching = result.scalar_one_or_none()

    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching not found",
        )

    return matching


@router.put("/{matching_id}", response_model=MatchingSchema)
async def update_matching(
    matching_id: UUID,
    update_data: MatchingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Matching:
    """Update a matching.

    Args:
        matching_id: Matching ID
        update_data: Update data
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Updated matching
    """
    result = await db.execute(
        select(Matching).where(Matching.id == matching_id)
    )
    matching = result.scalar_one_or_none()

    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching not found",
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(matching, field, value)

    await db.commit()
    await db.refresh(matching)

    return matching


@router.post("/{matching_id}/respond", response_model=MatchingSchema)
async def respond_to_matching(
    matching_id: UUID,
    response: MatchingExpertResponse,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Matching:
    """Expert response to matching proposal.

    Args:
        matching_id: Matching ID
        response: Expert's response (accept/reject)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated matching
    """
    result = await db.execute(
        select(Matching).where(Matching.id == matching_id)
    )
    matching = result.scalar_one_or_none()

    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching not found",
        )

    # Verify the expert is responding to their own matching
    result = await db.execute(
        select(Expert).where(Expert.id == matching.expert_id)
    )
    expert = result.scalar_one_or_none()

    if not expert or expert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only respond to your own matching proposals",
        )

    # Only allow response to PROPOSED matchings
    if matching.status != MatchingStatus.PROPOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only respond to proposed matchings",
        )

    # Update matching
    matching.status = MatchingStatus.ACCEPTED if response.accept else MatchingStatus.REJECTED
    matching.expert_response = response.response_message
    matching.expert_responded_at = datetime.utcnow().isoformat()

    await db.commit()
    await db.refresh(matching)

    return matching


@router.post("/{matching_id}/feedback", response_model=MatchingSchema)
async def submit_feedback(
    matching_id: UUID,
    feedback: MatchingCompanyFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Matching:
    """Submit company feedback for completed matching.

    Args:
        matching_id: Matching ID
        feedback: Company feedback and rating
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Updated matching
    """
    result = await db.execute(
        select(Matching).where(Matching.id == matching_id)
    )
    matching = result.scalar_one_or_none()

    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching not found",
        )

    # Update feedback
    matching.company_feedback = feedback.feedback
    matching.company_rating = feedback.rating
    matching.status = MatchingStatus.COMPLETED

    await db.commit()
    await db.refresh(matching)

    return matching


@router.delete("/{matching_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_matching(
    matching_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> None:
    """Soft delete a matching.

    Args:
        matching_id: Matching ID
        db: Database session
        current_user: Current operator/admin user
    """
    result = await db.execute(
        select(Matching).where(Matching.id == matching_id)
    )
    matching = result.scalar_one_or_none()

    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching not found",
        )

    matching.is_active = False
    await db.commit()


# ==============================================================================
# Sprint 6: Intelligent Matching Endpoints
# ==============================================================================


@router.post("/recommend", response_model=RecommendResponse)
async def get_intelligent_recommendations(
    request: RecommendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> RecommendResponse:
    """Get intelligent expert recommendations for a demand.

    Uses the enhanced matching algorithm that considers:
    - Specialty match (40%)
    - Qualification status (15%)
    - Career experience (15%)
    - Evaluation performance (20%)
    - Availability (10%)

    Args:
        request: Recommend request with demand_id and parameters
        db: Database session
        current_user: Current operator/admin user

    Returns:
        List of recommended candidates with detailed scores
    """
    # Get demand for title
    demand_result = await db.execute(
        select(Demand).where(Demand.id == request.demand_id)
    )
    demand = demand_result.scalar_one_or_none()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    try:
        # Use MatchingService for intelligent recommendations
        candidates = await MatchingService.find_best_matches(
            db=db,
            demand_id=request.demand_id,
            top_n=request.top_n,
            min_score=request.min_score,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    # Convert to response format
    recommended_candidates = []
    for candidate in candidates:
        # Get expert for specialties
        expert_result = await db.execute(
            select(Expert).where(Expert.id == candidate.expert_id)
        )
        expert = expert_result.scalar_one_or_none()

        recommended_candidates.append(
            RecommendedCandidate(
                expert_id=candidate.expert_id,
                expert_name=candidate.expert_name,
                total_score=candidate.score.total_score,
                score_breakdown=MatchScoreBreakdown(
                    specialty=candidate.score.specialty_score,
                    qualification=candidate.score.qualification_score,
                    career=candidate.score.career_score,
                    evaluation=candidate.score.evaluation_score,
                    availability=candidate.score.availability_score,
                ),
                recommendation_reasons=candidate.recommendation_reasons,
                specialties=expert.specialties if expert else None,
                qualification_status=expert.qualification_status.value if expert else "UNKNOWN",
            )
        )

    return RecommendResponse(
        demand_id=request.demand_id,
        demand_title=demand.title if hasattr(demand, 'title') else None,
        candidates=recommended_candidates,
        total_candidates=len(recommended_candidates),
        algorithm_version="v1.0",
    )


@router.get("/compatibility/{expert_id}/{demand_id}", response_model=CompatibilityCheckResponse)
async def check_compatibility(
    expert_id: UUID,
    demand_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> CompatibilityCheckResponse:
    """Check compatibility between a specific expert and demand.

    Returns detailed scoring breakdown and recommendation.

    Args:
        expert_id: Expert UUID
        demand_id: Demand UUID
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Compatibility analysis with scores and recommendation
    """
    try:
        result = await MatchingService.check_compatibility(
            db=db,
            expert_id=expert_id,
            demand_id=demand_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    # Convert score breakdown
    breakdown = result["score_breakdown"]

    return CompatibilityCheckResponse(
        expert_id=result["expert_id"],
        demand_id=result["demand_id"],
        total_score=result["total_score"],
        score_breakdown=MatchScoreBreakdown(
            specialty=breakdown["specialty"],
            qualification=breakdown["qualification"],
            career=breakdown["career"],
            evaluation=breakdown["evaluation"],
            availability=breakdown["availability"],
        ),
        recommendation=result["recommendation"],
        recommendation_text=result["recommendation_text"],
        reasons=result["reasons"],
        details=result["details"],
    )


@router.get("/analytics", response_model=MatchingAnalytics)
async def get_matching_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> MatchingAnalytics:
    """Get matching analytics and statistics.

    Returns comprehensive matching performance data including:
    - Status distribution
    - Success rate
    - Average match score
    - Top matched experts

    Args:
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Matching analytics data
    """
    analytics = await MatchingService.get_matching_analytics(db)

    return MatchingAnalytics(
        status_distribution=analytics["status_distribution"],
        success_rate=analytics["success_rate"],
        average_match_score=analytics["average_match_score"],
        total_active_matchings=analytics["total_active_matchings"],
        total_completed=analytics["total_completed"],
        top_matched_experts=analytics["top_matched_experts"],
    )
