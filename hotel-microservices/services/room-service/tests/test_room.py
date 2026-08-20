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
    assert len(rooms) == 3
    assert {room["id"] for room in rooms} == {101, 102, 201}


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
