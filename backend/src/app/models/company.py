"""Company (Demand) model for companies seeking expert matching."""
import enum
import uuid
from sqlalchemy import Enum, ForeignKey, String, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class CompanySize(str, enum.Enum):
    """Company size enum."""

    STARTUP = "STARTUP"  # 스타트업 (50인 미만)
    SMALL = "SMALL"  # 소기업 (50-100인)
    MEDIUM = "MEDIUM"  # 중기업 (100-300인)
    LARGE = "LARGE"  # 대기업 (300인 이상)


class IndustryType(str, enum.Enum):
    """Industry type enum."""

    MANUFACTURING = "MANUFACTURING"  # 제조업
    IT = "IT"  # IT/소프트웨어
    FINANCE = "FINANCE"  # 금융
    HEALTHCARE = "HEALTHCARE"  # 헬스케어
    LOGISTICS = "LOGISTICS"  # 물류
    RETAIL = "RETAIL"  # 유통/소매
    ENERGY = "ENERGY"  # 에너지
    OTHER = "OTHER"  # 기타


class DemandStatus(str, enum.Enum):
    """Demand request status enum."""

    PENDING = "PENDING"  # 대기중
    MATCHED = "MATCHED"  # 매칭완료
    IN_PROGRESS = "IN_PROGRESS"  # 진행중
    COMPLETED = "COMPLETED"  # 완료
    CANCELLED = "CANCELLED"  # 취소


class Company(Base, UUIDMixin, TimestampMixin):
    """Company model representing demand companies.

    Companies that request expert matching for smart factory consulting.
    """

    __tablename__ = "companies"

    # Basic information
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    industry: Mapped[IndustryType] = mapped_column(
        Enum(IndustryType), nullable=False, default=IndustryType.MANUFACTURING
    )
    size: Mapped[CompanySize] = mapped_column(
        Enum(CompanySize), nullable=False, default=CompanySize.SMALL
    )
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Contact information
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Company details
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Registration info
    registered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, industry={self.industry.value})>"


class Demand(Base, UUIDMixin, TimestampMixin):
    """Demand model representing company's expert request.

    A demand is a specific request from a company for expert consultation.
    """

    __tablename__ = "demands"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Demand details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Required specialties (list of specialty codes)
    required_specialties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Preferred expert count
    expert_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Project details
    project_duration: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "3개월"
    budget_range: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "5000만원-1억원"

    # Additional requirements
    requirements: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Status
    status: Mapped[DemandStatus] = mapped_column(
        Enum(DemandStatus), nullable=False, default=DemandStatus.PENDING
    )

    # Priority (1-5, higher is more urgent)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Demand(id={self.id}, company_id={self.company_id}, status={self.status.value})>"
