"""Pytest configuration and fixtures."""
import pytest
from uuid import uuid4
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from src.app.db.base import Base
from src.app.models.user import User, UserRole, UserStatus
from src.app.models.expert import Expert, DegreeType, OrgType, QualificationStatus
from src.app.core.security import get_password_hash, create_access_token
from src.main import app


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        name="Test User",
        role=UserRole.APPLICANT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_operator(db_session: AsyncSession):
    """Create a test operator user."""
    user = User(
        email="operator@example.com",
        password_hash=get_password_hash("operatorpass123"),
        name="Test Operator",
        role=UserRole.OPERATOR,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_expert(db_session: AsyncSession, test_user: User):
    """Create a test expert."""
    expert = Expert(
        user_id=test_user.id,
        degree_type=DegreeType.PHD,
        degree_field="Computer Science",
        career_years=5,
        position="Professor",
        org_name="Test University",
        org_type=OrgType.UNIVERSITY,
        specialties=["ML", "DL"],
        certifications=[],
        qualification_status=QualificationStatus.PENDING,
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)
    return expert


@pytest.fixture
def test_expert_id(test_expert: Expert) -> str:
    """Get test expert ID as string."""
    return str(test_expert.id)


# API Test Fixtures
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def user_token_headers(test_user: User) -> dict:
    """Create authorization headers for test user."""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def operator_token_headers(test_operator: User) -> dict:
    """Create authorization headers for test operator."""
    access_token = create_access_token(data={"sub": str(test_operator.id)})
    return {"Authorization": f"Bearer {access_token}"}
