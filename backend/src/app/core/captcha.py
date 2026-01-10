"""CAPTCHA verification utilities using Google reCAPTCHA v3."""
import logging
from typing import Optional

import httpx
from fastapi import HTTPException, status

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_recaptcha(token: str, action: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v3 token.

    Args:
        token: reCAPTCHA token from frontend
        action: Expected action (optional, for additional validation)

    Returns:
        True if verification passed, False otherwise

    Raises:
        HTTPException: If verification fails and RECAPTCHA_ENABLED is True
    """
    # Skip verification if disabled
    if not settings.RECAPTCHA_ENABLED:
        logger.debug("reCAPTCHA verification skipped (disabled)")
        return True

    if not token:
        if settings.RECAPTCHA_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reCAPTCHA 토큰이 필요합니다.",
            )
        return True

    if not settings.RECAPTCHA_SECRET_KEY:
        logger.warning("reCAPTCHA secret key not configured")
        return True

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                },
            )
            result = response.json()

        if not result.get("success"):
            error_codes = result.get("error-codes", [])
            logger.warning(f"reCAPTCHA verification failed: {error_codes}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reCAPTCHA 검증에 실패했습니다. 페이지를 새로고침 후 다시 시도해주세요.",
            )

        score = result.get("score", 0)
        if score < settings.RECAPTCHA_MIN_SCORE:
            logger.warning(f"reCAPTCHA score too low: {score}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자동화된 요청으로 감지되었습니다. 나중에 다시 시도해주세요.",
            )

        # Optionally verify action
        if action and result.get("action") != action:
            logger.warning(
                f"reCAPTCHA action mismatch: expected {action}, got {result.get('action')}"
            )
            # This is a soft warning, not a hard failure
            pass

        logger.debug(f"reCAPTCHA verification passed with score: {score}")
        return True

    except httpx.HTTPError as e:
        logger.error(f"reCAPTCHA verification HTTP error: {e}")
        # On network error, allow the request to proceed (fail-open)
        # In production, you might want to fail-closed instead
        return True

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {e}")
        return True
