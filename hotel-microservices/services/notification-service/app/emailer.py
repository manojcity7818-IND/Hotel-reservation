import html
import os
import smtplib
from email.message import EmailMessage
from typing import Union


class EmailDeliveryError(Exception):
    """Raised when SMTP cannot deliver a booking email."""


def smtp_settings() -> dict[str, Union[str, int, bool]]:
    return {
        "host": os.getenv("SMTP_HOST", "mailpit"),
        "port": int(os.getenv("SMTP_PORT", "1025")),
        "from_addr": os.getenv("SMTP_FROM", "Aryanstays <noreply@aryanstays.local>"),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "starttls": os.getenv("SMTP_STARTTLS", "false").lower() in {"1", "true", "yes"},
    }


def send_email(recipient: str, subject: str, message: str) -> None:
    settings = smtp_settings()
    body = EmailMessage()
    body["Subject"] = subject
    body["From"] = str(settings["from_addr"])
    body["To"] = recipient
    body.set_content(message)
    escaped = html.escape(message).replace("\n", "<br>")
    body.add_alternative(
        f"""<html><body style="font-family:Segoe UI,Arial,sans-serif;color:#1a2b49">
        <h2 style="color:#d63b7a">Aryanstays</h2>
        <p>{escaped}</p>
        <p style="color:#6b7280;font-size:13px">This booking alert was sent by Notification Service.</p>
        </body></html>""",
        subtype="html",
    )
    try:
        with smtplib.SMTP(
            str(settings["host"]), int(settings["port"]), timeout=8
        ) as smtp:
            if settings["starttls"]:
                smtp.starttls()
            if settings["user"]:
                smtp.login(str(settings["user"]), str(settings["password"]))
            smtp.send_message(body)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError(str(exc) or "SMTP delivery failed.") from exc
