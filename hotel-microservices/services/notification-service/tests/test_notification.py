from unittest.mock import patch

from fastapi.testclient import TestClient

from app import data
from app.emailer import EmailDeliveryError
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def setup_function() -> None:
    data.reset_data()


def test_create_booking_notification() -> None:
    payload = {
        "booking_id": 1,
        "event": "BOOKING_CREATED",
        "channel": "EMAIL",
        "recipient": "john@example.com",
        "subject": "Booking received",
        "message": "Pay to confirm booking 1.",
    }
    with patch("app.main.send_email") as send_email:
        response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["notification_id"] == 1
    assert body["status"] == "SENT"
    assert body["event"] == "BOOKING_CREATED"
    assert body["error"] is None
    send_email.assert_called_once_with(
        "john@example.com", "Booking received", "Pay to confirm booking 1."
    )


def test_email_delivery_failure_is_recorded() -> None:
    with patch(
        "app.main.send_email",
        side_effect=EmailDeliveryError("connection refused"),
    ):
        response = client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 3,
                "event": "BOOKING_CREATED",
                "recipient": "guest@example.com",
                "subject": "Booking received",
                "message": "Pay to confirm.",
            },
        )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "FAILED"
    assert "connection refused" in body["error"]


def test_list_notifications_by_booking() -> None:
    with patch("app.main.send_email"):
        client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 1,
                "event": "BOOKING_CREATED",
                "recipient": "a@example.com",
                "subject": "Created",
                "message": "Created",
            },
        )
        client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 2,
                "event": "BOOKING_CONFIRMED",
                "recipient": "b@example.com",
                "subject": "Confirmed",
                "message": "Confirmed",
            },
        )
    response = client.get("/api/v1/notifications", params={"booking_id": 1})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["booking_id"] == 1


def test_get_notification() -> None:
    with patch("app.main.send_email"):
        created = client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 9,
                "event": "BOOKING_CANCELLED",
                "recipient": "c@example.com",
                "subject": "Cancelled",
                "message": "Cancelled",
            },
        ).json()
    response = client.get(f"/api/v1/notifications/{created['notification_id']}")
    assert response.status_code == 200
    assert response.json()["event"] == "BOOKING_CANCELLED"


def test_notification_not_found() -> None:
    response = client.get("/api/v1/notifications/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found."


def test_invalid_event() -> None:
    response = client.post(
        "/api/v1/notifications",
        json={
            "booking_id": 1,
            "event": "UNKNOWN",
            "recipient": "a@example.com",
            "subject": "Hi",
            "message": "Hi",
        },
    )
    assert response.status_code == 400


def test_health_and_ready() -> None:
    assert client.get("/health").json()["service"] == "notification-service"
    assert client.get("/ready").json()["status"] == "ready"


def test_sms_skips_smtp() -> None:
    with patch("app.main.send_email") as send_email:
        response = client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 4,
                "event": "BOOKING_CREATED",
                "channel": "SMS",
                "recipient": "+919999999999",
                "subject": "SMS alert",
                "message": "Reserved",
            },
        )
    assert response.status_code == 201
    assert response.json()["status"] == "SENT"
    send_email.assert_not_called()


def test_list_all_notifications() -> None:
    with patch("app.main.send_email"):
        client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 1,
                "event": "BOOKING_CREATED",
                "recipient": "a@example.com",
                "subject": "A",
                "message": "A",
            },
        )
        client.post(
            "/api/v1/notifications",
            json={
                "booking_id": 2,
                "event": "BOOKING_CONFIRMED",
                "recipient": "b@example.com",
                "subject": "B",
                "message": "B",
            },
        )
    response = client.get("/api/v1/notifications")
    assert len(response.json()) == 2


def test_missing_recipient() -> None:
    response = client.post(
        "/api/v1/notifications",
        json={
            "booking_id": 1,
            "event": "BOOKING_CREATED",
            "subject": "Hi",
            "message": "Hi",
        },
    )
    assert response.status_code == 400


def test_unhandled_error_returns_500() -> None:
    with patch("app.main.data.next_id", side_effect=RuntimeError("boom")):
        with patch("app.main.send_email"):
            response = client.post(
                "/api/v1/notifications",
                json={
                    "booking_id": 1,
                    "event": "BOOKING_CREATED",
                    "recipient": "a@example.com",
                    "subject": "Hi",
                    "message": "Hi",
                },
            )
    assert response.status_code == 500
