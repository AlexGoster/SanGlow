from __future__ import annotations

import logging
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class EmailConfig(BaseSettings):
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    from_email: str = Field(default="", alias="FROM_EMAIL")
    from_name: str = Field(default="SanGlow", alias="FROM_NAME")

    model_config = {"env_prefix": "", "extra": "ignore"}


def generate_verification_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def send_verification_email(to_email: str, code: str, username: str) -> bool:
    config = EmailConfig()
    if not config.smtp_user or not config.smtp_password:
        logger.warning("SMTP not configured - verification code: %s", code)
        return False

    try:
        msg = MIMEText(
            f"Hello {username}!\n\n"
            f"Your SanGlow verification code is: {code}\n\n"
            f"This code expires in 15 minutes.\n\n"
            f"If you did not register, ignore this email.",
            "plain",
            "utf-8",
        )
        msg["Subject"] = "SanGlow - Email Verification"
        msg["From"] = f"{config.from_name} <{config.from_email or config.smtp_user}>"
        msg["To"] = to_email

        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=15) as server:
            server.starttls()
            server.login(config.smtp_user, config.smtp_password)
            server.sendmail(config.smtp_user or config.from_email, to_email, msg.as_string())
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("Failed to send verification email: %s", e)
        return False


def verify_code(stored_code: str | None, stored_expires: datetime | None, input_code: str) -> bool:
    if not stored_code or not stored_expires:
        return False
    now = datetime.now(timezone.utc)
    expires = stored_expires if stored_expires.tzinfo else stored_expires.replace(tzinfo=timezone.utc)
    if now > expires:
        return False
    return secrets.compare_digest(stored_code, input_code.strip())
