from unittest.mock import MagicMock, patch

import pytest

from app.emailer import EmailDeliveryError, send_email, smtp_settings


def test_smtp_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_PORT", raising=False)
    settings = smtp_settings()
    assert settings["host"] == "mailpit"
    assert settings["port"] == 1025


def test_send_email_uses_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_HOST", "mailpit")
    monkeypatch.setenv("SMTP_PORT", "1025")
    monkeypatch.setenv("SMTP_STARTTLS", "false")
    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    smtp.__exit__.return_value = False
    with patch("app.emailer.smtplib.SMTP", return_value=smtp) as factory:
        send_email("guest@example.com", "Hello", "Your booking is ready.")
    factory.assert_called_once()
    smtp.send_message.assert_called_once()


def test_send_email_raises_on_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_HOST", "mailpit")
    with patch("app.emailer.smtplib.SMTP", side_effect=OSError("down")):
        with pytest.raises(EmailDeliveryError):
            send_email("guest@example.com", "Hello", "Body")


def test_send_email_uses_starttls_and_login(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_STARTTLS", "true")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    smtp.__exit__.return_value = False
    with patch("app.emailer.smtplib.SMTP", return_value=smtp):
        send_email("guest@example.com", "Hello", "Body")
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("bot@example.com", "secret")
    smtp.send_message.assert_called_once()


def test_send_email_wraps_smtp_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    import smtplib

    monkeypatch.setenv("SMTP_HOST", "mailpit")
    with patch(
        "app.emailer.smtplib.SMTP",
        side_effect=smtplib.SMTPException(""),
    ):
        with pytest.raises(EmailDeliveryError):
            send_email("guest@example.com", "Hello", "Body")


def test_smtp_settings_starttls_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_STARTTLS", "YES")
    assert smtp_settings()["starttls"] is True
    monkeypatch.setenv("SMTP_STARTTLS", "no")
    assert smtp_settings()["starttls"] is False
