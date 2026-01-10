"""Rate limiting utilities using Redis."""
import logging
from datetime import timedelta
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Redis for tracking request counts."""

    def __init__(
        self,
        redis_url: str = None,
        max_attempts: int = 5,
        window_seconds: int = 300,  # 5 minutes
        block_seconds: int = 900,  # 15 minutes block after exceeded
    ):
        """Initialize rate limiter.

        Args:
            redis_url: Redis connection URL
            max_attempts: Maximum attempts allowed in the window
            window_seconds: Time window for counting attempts
            block_seconds: How long to block after exceeding limit
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.block_seconds = block_seconds

    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        return redis.from_url(self.redis_url)

    def _get_key(self, identifier: str, action: str) -> str:
        """Generate Redis key for rate limiting.

        Args:
            identifier: Unique identifier (e.g., IP address, email)
            action: Action being rate limited (e.g., 'login', 'password_reset')

        Returns:
            Redis key string
        """
        return f"rate_limit:{action}:{identifier}"

    def _get_block_key(self, identifier: str, action: str) -> str:
        """Generate Redis key for blocked status.

        Args:
            identifier: Unique identifier
            action: Action being rate limited

        Returns:
            Redis key string for block status
        """
        return f"rate_limit_blocked:{action}:{identifier}"

    async def check_rate_limit(
        self,
        identifier: str,
        action: str = "login",
    ) -> tuple[bool, Optional[int]]:
        """Check if the identifier is rate limited.

        Args:
            identifier: Unique identifier (e.g., IP address)
            action: Action being rate limited

        Returns:
            Tuple of (is_allowed, remaining_attempts or seconds_until_unblock)
        """
        redis_client = await self._get_redis()

        try:
            block_key = self._get_block_key(identifier, action)

            # Check if blocked
            blocked_ttl = await redis_client.ttl(block_key)
            if blocked_ttl > 0:
                return False, blocked_ttl

            rate_key = self._get_key(identifier, action)

            # Get current count
            current_count = await redis_client.get(rate_key)
            current_count = int(current_count) if current_count else 0

            remaining = self.max_attempts - current_count
            return True, max(0, remaining)

        finally:
            await redis_client.close()

    async def record_attempt(
        self,
        identifier: str,
        action: str = "login",
        success: bool = False,
    ) -> tuple[bool, Optional[int]]:
        """Record an attempt and check if limit is exceeded.

        Args:
            identifier: Unique identifier
            action: Action being rate limited
            success: Whether the attempt was successful (resets counter if True)

        Returns:
            Tuple of (is_allowed, remaining_attempts or seconds_until_unblock)
        """
        redis_client = await self._get_redis()

        try:
            rate_key = self._get_key(identifier, action)
            block_key = self._get_block_key(identifier, action)

            # If successful, reset the counter
            if success:
                await redis_client.delete(rate_key)
                return True, self.max_attempts

            # Check if already blocked
            blocked_ttl = await redis_client.ttl(block_key)
            if blocked_ttl > 0:
                return False, blocked_ttl

            # Increment counter
            current_count = await redis_client.incr(rate_key)

            # Set expiry if this is the first attempt
            if current_count == 1:
                await redis_client.expire(rate_key, self.window_seconds)

            # Check if limit exceeded
            if current_count >= self.max_attempts:
                # Block the identifier
                await redis_client.setex(block_key, self.block_seconds, "1")
                await redis_client.delete(rate_key)  # Clean up counter
                return False, self.block_seconds

            remaining = self.max_attempts - current_count
            return True, remaining

        finally:
            await redis_client.close()

    async def reset(self, identifier: str, action: str = "login") -> None:
        """Reset rate limit for an identifier.

        Args:
            identifier: Unique identifier
            action: Action being rate limited
        """
        redis_client = await self._get_redis()

        try:
            rate_key = self._get_key(identifier, action)
            block_key = self._get_block_key(identifier, action)
            await redis_client.delete(rate_key)
            await redis_client.delete(block_key)
        finally:
            await redis_client.close()


# Default rate limiter instance for login
login_rate_limiter = RateLimiter(
    max_attempts=5,
    window_seconds=300,  # 5 minutes
    block_seconds=900,  # 15 minutes
)

# Rate limiter for password reset requests
password_reset_rate_limiter = RateLimiter(
    max_attempts=3,
    window_seconds=3600,  # 1 hour
    block_seconds=3600,  # 1 hour
)


def get_client_ip(request: Request) -> str:
    """Get client IP address from request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check for forwarded headers (for proxies/load balancers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def check_login_rate_limit(request: Request) -> None:
    """Check login rate limit for the request.

    Args:
        request: FastAPI request object

    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_ip = get_client_ip(request)
    is_allowed, value = await login_rate_limiter.check_rate_limit(client_ip, "login")

    if not is_allowed:
        minutes = value // 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"로그인 시도 횟수가 초과되었습니다. {minutes}분 후에 다시 시도해주세요.",
        )
