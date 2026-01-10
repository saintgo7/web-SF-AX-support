"""Authentication API endpoints."""
import secrets
from datetime import timedelta

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_active_user, get_db
from src.app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
)
from src.app.core.rate_limiter import (
    login_rate_limiter,
    password_reset_rate_limiter,
    get_client_ip,
    check_login_rate_limit,
)
from src.app.core.captcha import verify_recaptcha
from src.app.models.user import User
from src.app.schemas.user import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    User as UserSchema,
    PasswordResetRequest,
    PasswordResetVerify,
    PasswordResetResponse,
)
from src.app.services.email_service import email_service
from src.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """User login endpoint.

    Args:
        request: FastAPI request object (for rate limiting)
        credentials: Login credentials (email, password)
        db: Database session

    Returns:
        Login response with tokens and user info

    Raises:
        HTTPException: If credentials are invalid or rate limit exceeded
    """
    client_ip = get_client_ip(request)

    # Check rate limit before processing
    await check_login_rate_limit(request)

    # Verify CAPTCHA if token provided or if enabled
    if credentials.captcha_token:
        await verify_recaptcha(credentials.captcha_token, action="login")

    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        # Record failed attempt
        await login_rate_limiter.record_attempt(client_ip, "login", success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    # Record successful login (resets rate limit counter)
    await login_rate_limiter.record_attempt(client_ip, "login", success=True)

    # Determine token expiration based on remember_me flag
    if credentials.remember_me:
        access_expire_minutes = settings.REMEMBER_ME_ACCESS_TOKEN_EXPIRE_MINUTES
        refresh_expire_days = settings.REMEMBER_ME_REFRESH_TOKEN_EXPIRE_DAYS
    else:
        access_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        refresh_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    # Create tokens
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=access_expire_minutes),
    )
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=timedelta(days=refresh_expire_days),
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=access_expire_minutes * 60,
        user=UserSchema.model_validate(user),
    )


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """User registration endpoint.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If email already exists
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        phone=user_data.phone,
        role=user_data.role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """User logout endpoint.

    Args:
        current_user: Current authenticated user

    Returns:
        Logout confirmation message
    """
    # In a stateless JWT setup, logout is handled client-side by removing the token
    # For server-side token invalidation, you would implement a token blacklist here
    return {"message": "Successfully logged out"}


@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: Request,
    request_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """Request password reset email.

    Args:
        request: FastAPI request object (for rate limiting)
        request_data: Password reset request with email
        db: Database session

    Returns:
        Success message (always returns success to prevent email enumeration)

    Raises:
        HTTPException: If rate limit exceeded
    """
    client_ip = get_client_ip(request)

    # Check rate limit
    is_allowed, value = await password_reset_rate_limiter.check_rate_limit(
        client_ip, "password_reset"
    )
    if not is_allowed:
        minutes = value // 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"비밀번호 재설정 요청 횟수가 초과되었습니다. {minutes}분 후에 다시 시도해주세요.",
        )

    # Record attempt
    await password_reset_rate_limiter.record_attempt(client_ip, "password_reset")

    # Find user by email
    result = await db.execute(select(User).where(User.email == request_data.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration attacks
    if not user:
        return PasswordResetResponse(
            message="비밀번호 재설정 이메일을 발송했습니다. 이메일을 확인해주세요.",
            success=True,
        )

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)

    # Store token in Redis with expiration
    redis_client = redis.from_url(settings.REDIS_URL)
    token_key = f"password_reset:{reset_token}"
    await redis_client.setex(
        token_key,
        settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES * 60,
        str(user.id),
    )
    await redis_client.close()

    # Send password reset email
    await email_service.send_password_reset_email(user.email, reset_token)

    return PasswordResetResponse(
        message="비밀번호 재설정 이메일을 발송했습니다. 이메일을 확인해주세요.",
        success=True,
    )


@router.post("/password-reset/verify", response_model=PasswordResetResponse)
async def verify_password_reset(
    verify_data: PasswordResetVerify,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """Verify reset token and update password.

    Args:
        verify_data: Token and new password
        db: Database session

    Returns:
        Success or error message

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Verify token from Redis
    redis_client = redis.from_url(settings.REDIS_URL)
    token_key = f"password_reset:{verify_data.token}"
    user_id = await redis_client.get(token_key)

    if not user_id:
        await redis_client.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않거나 만료된 토큰입니다.",
        )

    # Find user
    user_id_str = user_id.decode("utf-8") if isinstance(user_id, bytes) else user_id
    result = await db.execute(select(User).where(User.id == user_id_str))
    user = result.scalar_one_or_none()

    if not user:
        await redis_client.delete(token_key)
        await redis_client.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    # Update password
    user.password_hash = get_password_hash(verify_data.new_password)
    await db.commit()

    # Delete used token
    await redis_client.delete(token_key)
    await redis_client.close()

    return PasswordResetResponse(
        message="비밀번호가 성공적으로 변경되었습니다.",
        success=True,
    )
