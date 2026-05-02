import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Send password reset email using SMTP.
    Returns True if email was sent successfully, False otherwise.
    """
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Réinitialisation de votre mot de passe"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        # Email body
        body = f"""
Votre code de réinitialisation est : {reset_token}
Valide 15 minutes.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Send email
        if settings.SMTP_USE_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        server.quit()

        logger.info(f"Password reset email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {str(e)}")
        # In development, log the token for testing
        logger.warning(f"DEV MODE - Reset token for {to_email}: {reset_token}")
        return False


def send_invite_email(to_email: str, invite_link: str) -> bool:
    """
    Send invitation email using SMTP.
    Returns True if email was sent successfully, False otherwise.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "You're invited to DigMaco Analytics"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        text_body = f"""
    Welcome to DigMaco Analytics,

    An administrator invited you to join the platform as an Analyst.
    Click the link below to complete your registration:

    {invite_link}

    If you did not request this invitation, please ignore this email.
    """
        html_body = f"""
    <p>Welcome to <strong>DigMaco Analytics</strong>,</p>
    <p>An administrator invited you to join the platform as an Analyst.</p>
    <p>
      <a href=\"{invite_link}\" target=\"_blank\" rel=\"noreferrer\">Complete your registration</a>
    </p>
    <p>If you did not request this invitation, please ignore this email.</p>
    """
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if settings.SMTP_USE_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        server.quit()

        logger.info(f"Invite email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send invite email to {to_email}: {str(e)}")
        logger.warning(f"DEV MODE - Invite link for {to_email}: {invite_link}")
        return False
