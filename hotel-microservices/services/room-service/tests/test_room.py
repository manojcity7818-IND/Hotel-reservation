from fastapi.testclient import TestClient

from app import data
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def setup_function() -> None:
    data.reset_data()


def test_get_rooms() -> None:
    response = client.get("/api/v1/rooms")
    assert response.status_code == 200
    rooms = response.json()
    assert {101, 102, 201}.issubset({room["id"] for room in rooms})
    assert len(rooms) >= 3


def test_get_rooms_by_hotel() -> None:
    response = client.get("/api/v1/rooms/hotel/1")
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 2
    assert all(room["hotel_id"] == 1 for room in rooms)


def test_check_availability() -> None:
    response = client.get("/api/v1/rooms/101/availability")
    assert response.status_code == 200
    body = response.json()
    assert body["room_id"] == 101
    assert body["available"] is True


def test_reserve_room() -> None:
    response = client.post("/api/v1/rooms/101/reserve")
    assert response.status_code == 200
    assert response.json()["available"] is False
    availability = client.get("/api/v1/rooms/101/availability")
    assert availability.json()["available"] is False


def test_release_room() -> None:
    client.post("/api/v1/rooms/101/reserve")
    response = client.post("/api/v1/rooms/101/release")
    assert response.status_code == 200
    assert response.json()["available"] is True


def test_prevent_double_reservation() -> None:
    first = client.post("/api/v1/rooms/101/reserve")
    second = client.post("/api/v1/rooms/101/reserve")
    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"] == "Room is already reserved."


def test_room_not_found() -> None:
    response = client.get("/api/v1/rooms/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found."


def test_health_and_ready() -> None:
    health = client.get("/health")
    ready = client.get("/ready")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy", "service": "room-service"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready", "service": "room-service"}


def test_create_room() -> None:
    payload = {
        "hotel_id": 1,
        "room_number": "103",
        "room_type": "Suite",
        "price_per_night": 8000,
        "available": True,
    }
    response = client.post("/api/v1/rooms", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["room_number"] == "103"
    assert body["available"] is True


def test_update_room() -> None:
    payload = {
        "hotel_id": 1,
        "room_number": "101A",
        "room_type": "Deluxe",
        "price_per_night": 5500,
        "available": True,
    }
    response = client.put("/api/v1/rooms/101", json=payload)
    assert response.status_code == 200
    assert response.json()["room_number"] == "101A"
    assert response.json()["price_per_night"] == 5500


def test_delete_room() -> None:
    response = client.delete("/api/v1/rooms/102")
    assert response.status_code == 204
    assert client.get("/api/v1/rooms/102").status_code == 404


def test_release_when_not_reserved() -> None:
    response = client.post("/api/v1/rooms/101/release")
    assert response.status_code == 409
    assert response.json()["detail"] == "Room is not currently reserved."


def test_get_room_by_id() -> None:
    response = client.get("/api/v1/rooms/201")
    assert response.status_code == 200
    assert response.json()["hotel_id"] == 2


def test_create_room_invalid_price() -> None:
    payload = {
        "hotel_id": 1,
        "room_number": "104",
        "room_type": "Standard",
        "price_per_night": 0,
    }
    response = client.post("/api/v1/rooms", json=payload)
    assert response.status_code == 400
