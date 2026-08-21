import os

import httpx

NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL", "http://notification-service:8000"
)
TIMEOUT_SECONDS = 5.0


class NotificationServiceError(Exception):
    """Raised when Notification Service cannot be reached."""


def _client() -> httpx.Client:
    return httpx.Client(base_url=NOTIFICATION_SERVICE_URL, timeout=TIMEOUT_SECONDS)


def send_notification(payload: dict) -> dict | None:
    try:
        with _client() as client:
            response = client.post("/api/v1/notifications", json=payload)
    except httpx.RequestError:
        return None

    if response.status_code >= 500:
        return None
    if response.status_code != 201:
        return None
    return response.json()


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
