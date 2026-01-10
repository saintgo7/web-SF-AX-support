"""Expert management API endpoints."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.api.deps import get_current_active_user, get_current_operator, get_db
from src.app.models.user import User
from src.app.models.expert import Expert, DegreeType, OrgType, QualificationStatus
from src.app.schemas.expert import (
    ExpertCreate,
    ExpertUpdate,
    Expert as ExpertSchema,
    QualificationVerifyRequest,
    QualificationVerifyResponse,
    QualificationCheck,
)

router = APIRouter(prefix="/experts", tags=["Experts"])


def verify_qualification_rules(
    degree_type: DegreeType | None,
    degree_field: str | None,
    career_years: int | None,
    position: str | None,
    org_type: OrgType | None,
    certifications: list[dict] | None,
) -> tuple[QualificationStatus, dict[str, QualificationCheck]]:
    """Verify expert qualification based on rules.

    Args:
        degree_type: Type of degree
        degree_field: Field of study
        career_years: Years of experience
        position: Current position
        org_type: Type of organization
        certifications: List of certifications

    Returns:
        Tuple of qualification status and detailed check results
    """
    checks = {}

    # Related fields for AI/Smart Factory
    related_fields = [
        "컴퓨터공학",
        "데이터공학",
        "AI",
        "인공지능",
        "머신러닝",
        "딥러닝",
        "데이터사이언스",
        "전기전자공학",
        "기계공학",
        "산업공학",
        "통계학",
        "컴퓨터",
        "소프트웨어",
    ]

    def is_related_field(field: str | None) -> bool:
        """Check if field is related to AI/Smart Factory."""
        if not field:
            return False
        return any(related in field for related in related_fields)

    # Check 1: Degree + Field + Career combination
    degree_field_career_qualified = False

    if degree_type and is_related_field(degree_field) and career_years is not None:
        if degree_type == DegreeType.PHD and career_years >= 3:
            degree_field_career_qualified = True
            checks["degree_field_career"] = QualificationCheck(
                passed=True,
                reason=f"박사학위 + {degree_field} 관련분야 + {career_years}년 경력 (요구 3년 이상)"
            )
        elif degree_type == DegreeType.MASTER and career_years >= 5:
            degree_field_career_qualified = True
            checks["degree_field_career"] = QualificationCheck(
                passed=True,
                reason=f"석사학위 + {degree_field} 관련분야 + {career_years}년 경력 (요구 5년 이상)"
            )
        elif degree_type == DegreeType.BACHELOR and career_years >= 7:
            degree_field_career_qualified = True
            checks["degree_field_career"] = QualificationCheck(
                passed=True,
                reason=f"학사학위 + {degree_field} 관련분야 + {career_years}년 경력 (요구 7년 이상)"
            )
        else:
            required_years = {DegreeType.PHD: 3, DegreeType.MASTER: 5, DegreeType.BACHELOR: 7}.get(degree_type, 7)
            checks["degree_field_career"] = QualificationCheck(
                passed=False,
                reason=f"{degree_type.value}학위 + {degree_field} 관련분야 이지만 경력 {career_years}년 < 요구 {required_years}년"
            )
    else:
        checks["degree_field_career"] = QualificationCheck(
            passed=False,
            reason="학위 + 관련분야 + 경력 조건 미충족 (박사/석사/학사 + 관련분야 + 해당 경력 필요)"
        )

    # Check 2: High-level position or special certification
    high_level_positions = ["교수", "부교수", "정교수", "조교수", "전임강사", "연구원", "책임", "선임", "수석", "부장", "팀장", "이사", "대표"]
    is_high_level_position = position and any(pos in position for pos in high_level_positions)
    is_university_faculty = org_type == OrgType.UNIVERSITY and position and ("교수" in position or "연구원" in position)

    has_high_level_cert = False
    if certifications:
        for cert in certifications:
            cert_name = cert.get("name", "").lower()
            if "특급" in cert_name or "기술사" in cert_name:
                has_high_level_cert = True
                break

    if is_high_level_position or is_university_faculty:
        checks["position_certification"] = QualificationCheck(
            passed=True,
            reason=f"직급/직위 요건 충족 ({position}, {org_type.value if org_type else ''})"
        )
    elif has_high_level_cert:
        checks["position_certification"] = QualificationCheck(
            passed=True,
            reason="특급기술자 또는 기술사 자격 보유"
        )
    else:
        checks["position_certification"] = QualificationCheck(
            passed=False,
            reason="직급/직위 요건 미충족 (부장급 이상 또는 대학 전임강사 이상 또는 특급기술자 필요)"
        )

    # Determine final status according to plan rules
    position_cert_qualified = checks["position_certification"].passed

    if degree_field_career_qualified or position_cert_qualified:
        final_status = QualificationStatus.QUALIFIED
        qualification_note = "자격요건 충족"
    else:
        final_status = QualificationStatus.DISQUALIFIED
        qualification_note = "자격요건 미충족"

    # Add overall note
    checks["overall"] = QualificationCheck(
        passed=(final_status == QualificationStatus.QUALIFIED),
        reason=qualification_note
    )

    return final_status, checks


@router.post("", response_model=ExpertSchema, status_code=status.HTTP_201_CREATED)
async def create_expert(
    expert_data: ExpertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Expert:
    """Create expert profile.

    Args:
        expert_data: Expert creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created expert profile

    Raises:
        HTTPException: If expert profile already exists
    """
    # Check if expert profile already exists
    result = await db.execute(select(Expert).where(Expert.user_id == expert_data.user_id))
    existing_expert = result.scalar_one_or_none()

    if existing_expert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expert profile already exists for this user",
        )

    # Create new expert
    new_expert = Expert(
        user_id=expert_data.user_id,
        degree_type=expert_data.degree_type,
        degree_field=expert_data.degree_field,
        career_years=expert_data.career_years,
        position=expert_data.position,
        org_name=expert_data.org_name,
        org_type=expert_data.org_type,
        specialties=expert_data.specialties,
        certifications=expert_data.certifications,
    )

    db.add(new_expert)
    await db.commit()
    await db.refresh(new_expert)

    return new_expert


@router.get("/{expert_id}", response_model=ExpertSchema)
async def get_expert(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Expert:
    """Get expert by ID.

    Args:
        expert_id: Expert ID
        db: Database session

    Returns:
        Expert profile

    Raises:
        HTTPException: If expert not found
    """
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    return expert


@router.put("/{expert_id}", response_model=ExpertSchema)
async def update_expert(
    expert_id: UUID,
    expert_data: ExpertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Expert:
    """Update expert profile.

    Args:
        expert_id: Expert ID
        expert_data: Expert update data
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Updated expert profile

    Raises:
        HTTPException: If expert not found
    """
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    # Update fields
    for field, value in expert_data.model_dump(exclude_unset=True).items():
        setattr(expert, field, value)

    await db.commit()
    await db.refresh(expert)

    return expert


@router.post("/qualification/verify", response_model=QualificationVerifyResponse)
async def verify_qualification(
    request_data: QualificationVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> QualificationVerifyResponse:
    """Verify expert qualification automatically (dry run).

    This endpoint performs verification without updating the database.
    Use /{expert_id}/qualification/verify to verify and save.

    Args:
        request_data: Qualification verification request data
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Qualification verification result
    """
    # Run qualification verification logic
    status, checks = verify_qualification_rules(
        degree_type=request_data.degree_type,
        degree_field=request_data.degree_field,
        career_years=request_data.career_years,
        position=request_data.position,
        org_type=request_data.org_type,
        certifications=request_data.certifications,
    )

    return QualificationVerifyResponse(
        expert_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder for dry run
        qualification_status=status,
        verification_details=checks,
        verified_at=datetime.utcnow(),
    )


@router.post("/{expert_id}/qualification/verify", response_model=ExpertSchema)
async def verify_expert_qualification(
    expert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Expert:
    """Verify and update expert qualification in database.

    Args:
        expert_id: Expert ID to verify
        db: Database session
        current_user: Current authenticated operator

    Returns:
        Updated expert profile with qualification status

    Raises:
        HTTPException: If expert not found
    """
    # Get expert profile
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    # Run qualification verification logic
    status, checks = verify_qualification_rules(
        degree_type=expert.degree_type,
        degree_field=expert.degree_field,
        career_years=expert.career_years,
        position=expert.position,
        org_type=expert.org_type,
        certifications=expert.certifications,
    )

    # Update expert qualification status
    expert.qualification_status = status
    expert.qualification_note = checks["overall"].reason

    await db.commit()
    await db.refresh(expert)

    return expert
