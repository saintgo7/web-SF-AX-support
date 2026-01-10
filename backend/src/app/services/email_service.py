"""Email service for sending notifications."""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending various notifications."""

    @staticmethod
    async def send_password_reset_email(email: str, reset_token: str) -> bool:
        """Send password reset email.

        Args:
            email: Recipient email address
            reset_token: Password reset token

        Returns:
            True if email sent successfully, False otherwise
        """
        reset_url = f"http://localhost:3000/auth/reset-password?token={reset_token}"

        subject = "[AX 코칭단] 비밀번호 재설정 안내"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: 'Noto Sans KR', Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 30px;">
                <h2 style="color: #1a56db; margin-bottom: 24px;">비밀번호 재설정</h2>

                <p style="color: #4b5563; line-height: 1.6;">
                    안녕하세요,<br><br>
                    비밀번호 재설정을 요청하셨습니다. 아래 버튼을 클릭하여 새 비밀번호를 설정해주세요.
                </p>

                <div style="text-align: center; margin: 32px 0;">
                    <a href="{reset_url}"
                       style="background-color: #1a56db; color: #ffffff; padding: 12px 32px;
                              text-decoration: none; border-radius: 6px; font-weight: 600;">
                        비밀번호 재설정
                    </a>
                </div>

                <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                    이 링크는 30분 후에 만료됩니다.<br>
                    본인이 요청하지 않으셨다면 이 이메일을 무시해주세요.
                </p>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">

                <p style="color: #9ca3af; font-size: 12px;">
                    AX 코칭단 평가 시스템<br>
                    이 메일은 발신 전용입니다.
                </p>
            </div>
        </body>
        </html>
        """

        # In development mode, just log the email content
        if settings.is_dev or not settings.SMTP_HOST:
            logger.info("=" * 60)
            logger.info("[DEV MODE] Password Reset Email")
            logger.info(f"To: {email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Reset URL: {reset_url}")
            logger.info(f"Token: {reset_token}")
            logger.info("=" * 60)
            return True

        # Production mode: send real email via SMTP
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg["To"] = email

            msg.attach(MIMEText(html_content, "html", "utf-8"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, email, msg.as_string())

            logger.info(f"Password reset email sent to {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False


email_service = EmailService()
