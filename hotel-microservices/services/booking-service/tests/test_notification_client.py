from datetime import date
from typing import Optional
from unittest.mock import patch

import httpx

from app import notification_client
from app.models import Booking, BookingStatus


class _FakeResponse:
    def __init__(self, status_code: int, payload: Optional[dict] = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload

    @property
    def text(self) -> str:
        return str(self._payload)

    @property
    def text(self) -> str:
        return str(self._payload)


class _FakeClient:
    def __init__(self, response: _FakeResponse) -> None:
        self._response = response
        self.posted = None

    def __enter__(self) -> "_FakeClient":
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def post(self, path: str, json: dict) -> _FakeResponse:
        self.posted = (path, json)
        return self._response


def test_send_notification_success() -> None:
    response = _FakeResponse(201, {"notification_id": 1, "status": "SENT"})
    fake = _FakeClient(response)
    with patch.object(notification_client, "_client", return_value=fake):
        body = notification_client.send_notification(
            {
                "booking_id": 1,
                "event": "BOOKING_CREATED",
                "channel": "EMAIL",
                "recipient": "a@example.com",
                "subject": "Hi",
                "message": "Hi",
            }
        )
    assert body["notification_id"] == 1
    assert fake.posted[0] == "/api/v1/notifications"


def test_send_notification_unavailable() -> None:
    with patch.object(
        notification_client,
        "_client",
        side_effect=httpx.ConnectError("down"),
    ):
        assert notification_client.send_notification({"booking_id": 1}) is None


def test_notify_booking_payload() -> None:
    booking = Booking(
        booking_id=4,
        hotel_id=1,
        room_id=101,
        customer_name="Aryan",
        customer_email="aryan@example.com",
        check_in=date(2026, 9, 1),
        check_out=date(2026, 9, 3),
        status=BookingStatus.PENDING_PAYMENT,
        amount=9000,
    )
    response = _FakeResponse(201, {"notification_id": 8})
    fake = _FakeClient(response)
    with patch.object(notification_client, "_client", return_value=fake):
        notification_client.notify_booking(
            booking, "BOOKING_CONFIRMED", "Confirmed", "You are booked."
        )
    assert fake.posted[1]["recipient"] == "aryan@example.com"
    assert fake.posted[1]["event"] == "BOOKING_CONFIRMED"


def test_send_notification_server_error() -> None:
    fake = _FakeClient(_FakeResponse(500))
    with patch.object(notification_client, "_client", return_value=fake):
        assert notification_client.send_notification({"booking_id": 1}) is None


def test_send_notification_rejected() -> None:
    fake = _FakeClient(_FakeResponse(400, {"detail": "Invalid request."}))
    with patch.object(notification_client, "_client", return_value=fake):
        assert notification_client.send_notification({"booking_id": 1}) is None


def test_send_notification_failed_delivery_still_returns_body() -> None:
    fake = _FakeClient(
        _FakeResponse(201, {"notification_id": 2, "status": "FAILED", "error": "SMTP down"})
    )
    with patch.object(notification_client, "_client", return_value=fake):
        body = notification_client.send_notification({"booking_id": 1})
    assert body["status"] == "FAILED"
