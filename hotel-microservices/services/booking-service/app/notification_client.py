import logging
import os

import httpx

logger = logging.getLogger(__name__)

NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL", "http://notification-service:8000"
)
TIMEOUT_SECONDS = 8.0


class NotificationServiceError(Exception):
    """Raised when Notification Service cannot be reached."""


def _client() -> httpx.Client:
    return httpx.Client(base_url=NOTIFICATION_SERVICE_URL, timeout=TIMEOUT_SECONDS)


def send_notification(payload: dict) -> dict | None:
    try:
        with _client() as client:
            response = client.post("/api/v1/notifications", json=payload)
    except httpx.RequestError as exc:
        logger.warning("Notification Service is unreachable: %s", exc)
        return None

    if response.status_code >= 500:
        logger.warning("Notification Service returned %s", response.status_code)
        return None
    if response.status_code != 201:
        logger.warning("Notification Service rejected the email: %s", response.text)
        return None
    body = response.json()
    if body.get("status") == "FAILED":
        logger.warning("Booking email was not delivered: %s", body.get("error"))
    return body


def notify_booking(
    booking,
    event: str,
    subject: str,
    message: str,
) -> dict | None:
    return send_notification(
        {
            "booking_id": booking.booking_id,
            "event": event,
            "channel": "EMAIL",
            "recipient": booking.customer_email,
            "subject": subject,
            "message": message,
        }
    )
