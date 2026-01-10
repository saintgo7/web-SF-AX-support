"""User schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.app.models.user import UserRole, UserStatus


# Base schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: str | None = Field(None, max_length=20)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.APPLICANT


class UserUpdate(BaseModel):
    """User update schema."""

    name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, max_length=20)
    status: UserStatus | None = None


class UserInDB(UserBase):
    """User schema with database fields."""

    id: UUID
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class User(UserInDB):
    """User response schema."""

    pass


# Token schemas
class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: UUID  # user_id
    exp: int
    type: str = "access"


# Login schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str
    remember_me: bool = False
    captcha_token: str | None = None  # reCAPTCHA v3 token (optional)


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: User


# Password Reset schemas
class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordResetVerify(BaseModel):
    """Password reset verification schema."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordResetResponse(BaseModel):
    """Password reset response schema."""

    message: str
    success: bool = True
