"""Company and Demand management API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_active_user, get_current_operator, get_db
from src.app.models.user import User
from src.app.models.company import Company, Demand, DemandStatus
from src.app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    Company as CompanySchema,
    CompanyList,
    DemandCreate,
    DemandUpdate,
    Demand as DemandSchema,
    DemandList,
    DemandSummary,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


# Company endpoints
@router.post("", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Company:
    """Create a new company.

    Args:
        company_data: Company creation data
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Created company
    """
    # Check for duplicate business number
    if company_data.business_number:
        result = await db.execute(
            select(Company).where(Company.business_number == company_data.business_number)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this business number already exists",
            )

    company = Company(
        **company_data.model_dump(),
        registered_by=current_user.id,
    )

    db.add(company)
    await db.commit()
    await db.refresh(company)

    return company


@router.get("", response_model=CompanyList)
async def get_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CompanyList:
    """Get list of companies.

    Args:
        page: Page number
        page_size: Items per page
        search: Optional search term
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of companies
    """
    query = select(Company).where(Company.is_active == True)
    count_query = select(func.count()).select_from(Company).where(Company.is_active == True)

    if search:
        search_filter = Company.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Company.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    companies = result.scalars().all()

    return CompanyList(
        items=list(companies),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{company_id}", response_model=CompanySchema)
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Company:
    """Get a specific company.

    Args:
        company_id: Company ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Company details
    """
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


@router.put("/{company_id}", response_model=CompanySchema)
async def update_company(
    company_id: UUID,
    update_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Company:
    """Update a company.

    Args:
        company_id: Company ID
        update_data: Update data
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Updated company
    """
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> None:
    """Soft delete a company.

    Args:
        company_id: Company ID
        db: Database session
        current_user: Current operator/admin user
    """
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    company.is_active = False
    await db.commit()


# Demand endpoints
@router.post("/{company_id}/demands", response_model=DemandSchema, status_code=status.HTTP_201_CREATED)
async def create_demand(
    company_id: UUID,
    demand_data: DemandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Demand:
    """Create a new demand for a company.

    Args:
        company_id: Company ID
        demand_data: Demand creation data
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Created demand
    """
    # Verify company exists
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    demand = Demand(
        company_id=company_id,
        title=demand_data.title,
        description=demand_data.description,
        required_specialties=demand_data.required_specialties,
        expert_count=demand_data.expert_count,
        project_duration=demand_data.project_duration,
        budget_range=demand_data.budget_range,
        requirements=demand_data.requirements,
        priority=demand_data.priority,
    )

    db.add(demand)
    await db.commit()
    await db.refresh(demand)

    return demand


@router.get("/{company_id}/demands", response_model=DemandList)
async def get_company_demands(
    company_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DemandList:
    """Get demands for a specific company.

    Args:
        company_id: Company ID
        page: Page number
        page_size: Items per page
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of demands
    """
    query = select(Demand).where(
        Demand.company_id == company_id,
        Demand.is_active == True
    )
    count_query = select(func.count()).select_from(Demand).where(
        Demand.company_id == company_id,
        Demand.is_active == True
    )

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Demand.priority.desc(), Demand.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    demands = result.scalars().all()

    return DemandList(
        items=list(demands),
        total=total,
        page=page,
        page_size=page_size,
    )


# Demand routes (all demands across companies)
demands_router = APIRouter(prefix="/demands", tags=["Demands"])


@demands_router.get("", response_model=DemandList)
async def get_all_demands(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: DemandStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DemandList:
    """Get all demands.

    Args:
        page: Page number
        page_size: Items per page
        status_filter: Optional status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of demands
    """
    query = select(Demand).where(Demand.is_active == True)
    count_query = select(func.count()).select_from(Demand).where(Demand.is_active == True)

    if status_filter:
        query = query.where(Demand.status == status_filter)
        count_query = count_query.where(Demand.status == status_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Demand.priority.desc(), Demand.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    demands = result.scalars().all()

    return DemandList(
        items=list(demands),
        total=total,
        page=page,
        page_size=page_size,
    )


@demands_router.get("/summary", response_model=DemandSummary)
async def get_demand_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> DemandSummary:
    """Get demand summary statistics.

    Args:
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Demand summary statistics
    """
    result = await db.execute(
        select(Demand.status, func.count(Demand.id))
        .where(Demand.is_active == True)
        .group_by(Demand.status)
    )
    status_counts = dict(result.all())

    return DemandSummary(
        total=sum(status_counts.values()),
        pending=status_counts.get(DemandStatus.PENDING, 0),
        matched=status_counts.get(DemandStatus.MATCHED, 0),
        in_progress=status_counts.get(DemandStatus.IN_PROGRESS, 0),
        completed=status_counts.get(DemandStatus.COMPLETED, 0),
    )


@demands_router.get("/{demand_id}", response_model=DemandSchema)
async def get_demand(
    demand_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Demand:
    """Get a specific demand.

    Args:
        demand_id: Demand ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Demand details
    """
    result = await db.execute(
        select(Demand).where(Demand.id == demand_id)
    )
    demand = result.scalar_one_or_none()

    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    return demand


@demands_router.put("/{demand_id}", response_model=DemandSchema)
async def update_demand(
    demand_id: UUID,
    update_data: DemandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> Demand:
    """Update a demand.

    Args:
        demand_id: Demand ID
        update_data: Update data
        db: Database session
        current_user: Current operator/admin user

    Returns:
        Updated demand
    """
    result = await db.execute(
        select(Demand).where(Demand.id == demand_id)
    )
    demand = result.scalar_one_or_none()

    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(demand, field, value)

    await db.commit()
    await db.refresh(demand)

    return demand


@demands_router.delete("/{demand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_demand(
    demand_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_operator),
) -> None:
    """Soft delete a demand.

    Args:
        demand_id: Demand ID
        db: Database session
        current_user: Current operator/admin user
    """
    result = await db.execute(
        select(Demand).where(Demand.id == demand_id)
    )
    demand = result.scalar_one_or_none()

    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand not found",
        )

    demand.is_active = False
    await db.commit()
