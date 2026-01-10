"""Expert model."""
import enum
import uuid
from sqlalchemy import Enum, ForeignKey, String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class DegreeType(str, enum.Enum):
    """Degree type enum."""

    PHD = "PHD"
    MASTER = "MASTER"
    BACHELOR = "BACHELOR"


class OrgType(str, enum.Enum):
    """Organization type enum."""

    UNIVERSITY = "UNIVERSITY"
    COMPANY = "COMPANY"
    RESEARCH = "RESEARCH"
    OTHER = "OTHER"


class QualificationStatus(str, enum.Enum):
    """Qualification status enum."""

    PENDING = "PENDING"
    QUALIFIED = "QUALIFIED"
    DISQUALIFIED = "DISQUALIFIED"


class Expert(Base, UUIDMixin, TimestampMixin):
    """Expert model."""

    __tablename__ = "experts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    degree_type: Mapped[DegreeType | None] = mapped_column(Enum(DegreeType), nullable=True)
    degree_field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    career_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    org_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    org_type: Mapped[OrgType | None] = mapped_column(Enum(OrgType), nullable=True)
    specialties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # List[str]
    certifications: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # List[dict]
    qualification_status: Mapped[QualificationStatus] = mapped_column(
        Enum(QualificationStatus), nullable=False, default=QualificationStatus.PENDING
    )
    qualification_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Expert(id={self.id}, user_id={self.user_id}, status={self.qualification_status.value})>"
