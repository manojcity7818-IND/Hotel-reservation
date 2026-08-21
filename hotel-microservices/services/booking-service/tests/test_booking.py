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
    "amount": 10000,
}


def setup_function() -> None:
    data.reset_data()


def _create_booking():
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room"),
        patch("app.main.notification_client.notify_booking"),
    ):
        return client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)


def test_create_booking() -> None:
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room") as reserve,
        patch("app.main.notification_client.notify_booking") as notify,
    ):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["booking_id"] == 1
    assert body["status"] == "PENDING_PAYMENT"
    assert body["amount"] == 10000
    reserve.assert_called_once_with(101)
    notify.assert_called_once()
    assert notify.call_args.args[1] == "BOOKING_CREATED"


def test_complete_payment() -> None:
    created = _create_booking().json()
    with (
        patch(
            "app.main.payment_client.get_payment",
            return_value={"booking_id": created["booking_id"], "status": "SUCCESS"},
        ),
        patch("app.main.notification_client.notify_booking") as notify,
    ):
        response = client.post(
            f"/api/v1/bookings/{created['booking_id']}/pay",
            json={"payment_id": 77},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"
    assert response.json()["payment_id"] == 77
    notify.assert_called_once()
    assert notify.call_args.args[1] == "BOOKING_CONFIRMED"


def test_failed_payment_does_not_confirm() -> None:
    created = _create_booking().json()
    with (
        patch(
            "app.main.payment_client.get_payment",
            return_value={"booking_id": created["booking_id"], "status": "FAILED"},
        ),
        patch("app.main.notification_client.notify_booking") as notify,
    ):
        response = client.post(
            f"/api/v1/bookings/{created['booking_id']}/pay",
            json={"payment_id": 77},
        )
    assert response.status_code == 409
    assert client.get(f"/api/v1/bookings/{created['booking_id']}").json()["status"] == "PAYMENT_FAILED"
    notify.assert_called_once()
    assert notify.call_args.args[1] == "PAYMENT_FAILED"


def test_get_booking() -> None:
    created = _create_booking().json()
    response = client.get(f"/api/v1/bookings/{created['booking_id']}")
    assert response.status_code == 200
    assert response.json()["customer_name"] == "John Doe"


def test_cancel_booking() -> None:
    created = _create_booking().json()
    with (
        patch("app.main.room_client.release_room") as release,
        patch("app.main.notification_client.notify_booking") as notify,
    ):
        response = client.delete(f"/api/v1/bookings/{created['booking_id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    release.assert_called_once_with(101)
    notify.assert_called_once()
    assert notify.call_args.args[1] == "BOOKING_CANCELLED"


def test_prevent_booking_unavailable_room() -> None:
    with patch("app.main.room_client.get_availability", return_value=False):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)
    assert response.status_code == 409
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


def test_health_and_ready() -> None:
    assert client.get("/health").json() == {"status": "healthy", "service": "booking-service"}
    assert client.get("/ready").json()["status"] == "ready"


def test_list_bookings() -> None:
    _create_booking()
    response = client.get("/api/v1/bookings")
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "PENDING_PAYMENT"


def test_cancel_already_cancelled() -> None:
    created = _create_booking().json()
    with patch("app.main.room_client.release_room"):
        first = client.delete(f"/api/v1/bookings/{created['booking_id']}")
        second = client.delete(f"/api/v1/bookings/{created['booking_id']}")
    assert first.status_code == 200
    assert second.status_code == 409


def test_invalid_dates() -> None:
    payload = dict(BOOKING_PAYLOAD)
    payload["check_out"] = "2026-08-01"
    assert client.post("/api/v1/bookings", json=payload).status_code == 400


def test_invalid_email() -> None:
    payload = dict(BOOKING_PAYLOAD)
    payload["customer_email"] = "not-an-email"
    assert client.post("/api/v1/bookings", json=payload).status_code == 400


def test_missing_amount() -> None:
    payload = dict(BOOKING_PAYLOAD)
    payload.pop("amount")
    assert client.post("/api/v1/bookings", json=payload).status_code == 400


def test_pay_booking_not_found() -> None:
    response = client.post("/api/v1/bookings/999/pay", json={"payment_id": 1})
    assert response.status_code == 404


def test_pay_cancelled_booking() -> None:
    created = _create_booking().json()
    with patch("app.main.room_client.release_room"):
        client.delete(f"/api/v1/bookings/{created['booking_id']}")
    response = client.post(
        f"/api/v1/bookings/{created['booking_id']}/pay",
        json={"payment_id": 1},
    )
    assert response.status_code == 409
    assert "cancelled" in response.json()["detail"].lower()


def test_pay_already_confirmed() -> None:
    created = _create_booking().json()
    with (
        patch(
            "app.main.payment_client.get_payment",
            return_value={"booking_id": created["booking_id"], "status": "SUCCESS"},
        ),
        patch("app.main.notification_client.notify_booking"),
    ):
        first = client.post(
            f"/api/v1/bookings/{created['booking_id']}/pay",
            json={"payment_id": 77},
        )
        second = client.post(
            f"/api/v1/bookings/{created['booking_id']}/pay",
            json={"payment_id": 78},
        )
    assert first.status_code == 200
    assert second.status_code == 409
    assert "already paid" in second.json()["detail"].lower()


def test_payment_does_not_match_booking() -> None:
    created = _create_booking().json()
    with patch(
        "app.main.payment_client.get_payment",
        return_value={"booking_id": 999, "status": "SUCCESS"},
    ):
        response = client.post(
            f"/api/v1/bookings/{created['booking_id']}/pay",
            json={"payment_id": 77},
        )
    assert response.status_code == 409
    assert "does not match" in response.json()["detail"].lower()


def test_payment_service_unavailable() -> None:
    from app.payment_client import PaymentServiceError

    created = _create_booking().json()
    with patch(
        "app.main.payment_client.get_payment",
        side_effect=PaymentServiceError("Payment Service is unavailable."),
    ):
        response = client.post(
            f"/api/v1/bookings/{created['booking_id']}/pay",
            json={"payment_id": 77},
        )
    assert response.status_code == 503
    assert "payment" in response.json()["detail"].lower()


def test_cancel_booking_not_found() -> None:
    response = client.delete("/api/v1/bookings/999")
    assert response.status_code == 404


def test_create_booking_still_succeeds_if_email_fails() -> None:
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room"),
        patch("app.main.notification_client.notify_booking", return_value=None),
    ):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING_PAYMENT"


def test_unhandled_error_returns_500() -> None:
    with (
        patch("app.main.room_client.get_availability", return_value=True),
        patch("app.main.room_client.reserve_room"),
        patch("app.main.data.next_id", side_effect=RuntimeError("boom")),
    ):
        response = client.post("/api/v1/bookings", json=BOOKING_PAYLOAD)
    assert response.status_code == 500
