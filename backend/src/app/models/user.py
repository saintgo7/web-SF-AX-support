"""User model."""
import enum
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.base import Base, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    """User role enum."""

    APPLICANT = "APPLICANT"
    EVALUATOR = "EVALUATOR"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    """User status enum."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class User(Base, UUIDMixin, TimestampMixin):
    """User model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.APPLICANT, index=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
