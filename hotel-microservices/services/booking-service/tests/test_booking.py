from unittest.mock import patch

from fastapi.testclient import TestClient

from app import data
from app.main import app
from app.room_client import RoomServiceError

client = TestClient(app, raise_server_exceptions=False)

BOOKING_PAYLOAD = {
    "hotel_id": 1,
    "room_id": 101,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "check_in": "2026-09-01",
    "check_out": "2026-09-03",
}


def setup_function() -> None:
    data.reset_data()


def test_create_booking() -> None:
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room") as reserve,
    ):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["booking_id"] == 1
    assert body["status"] == "CONFIRMED"
    assert body["room_id"] == 101
    reserve.assert_called_once_with(101)


def test_get_booking() -> None:
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room"),
    ):
        created = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD).json()

    response = client.get(f"/api/v1/bookings/{created['booking_id']}")
    assert response.status_code == 200
    assert response.json()["customer_name"] == "John Doe"


def test_cancel_booking() -> None:
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room"),
    ):
        created = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD).json()

    with patch("app.main.room_client.release_room") as release:
        response = client.delete(f"/api/v1/bookings/{created['booking_id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    release.assert_called_once_with(101)


def test_prevent_booking_unavailable_room() -> None:
    with patch("app.main.room_client.get_availability", return_value=False):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot create booking because room is unavailable."
    assert client.get("/api/v1/bookings").json() == []


def test_handle_room_service_failure() -> None:
    with patch(
        "app.main.room_client.get_availability",
        side_effect=RoomServiceError("Room Service is unavailable."),
    ):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_booking_not_found() -> None:
    response = client.get("/api/v1/bookings/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found."


def test_health_and_ready() -> None:
    health = client.get("/health")
    ready = client.get("/ready")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy", "service": "booking-service"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready", "service": "booking-service"}
