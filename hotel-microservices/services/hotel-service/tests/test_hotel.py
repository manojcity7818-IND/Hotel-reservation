from fastapi.testclient import TestClient

from app import data
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def setup_function() -> None:
    data.reset_data()


def test_get_hotels() -> None:
    response = client.get("/api/v1/hotels")
    assert response.status_code == 200
    hotels = response.json()
    assert len(hotels) == 2
    assert hotels[0]["name"] == "Grand Hyderabad Hotel"


def test_get_hotel_by_id() -> None:
    response = client.get("/api/v1/hotels/1")
    assert response.status_code == 200
    hotel = response.json()
    assert hotel["id"] == 1
    assert hotel["city"] == "Hyderabad"


def test_create_hotel() -> None:
    payload = {"name": "Chennai Bay Hotel", "city": "Chennai", "rating": 4.0}
    response = client.post("/api/v1/hotels", json=payload)
    assert response.status_code == 201
    hotel = response.json()
    assert hotel["id"] == 3
    assert hotel["name"] == "Chennai Bay Hotel"


def test_update_hotel() -> None:
    payload = {"name": "Grand Hyderabad Hotel Deluxe", "city": "Hyderabad", "rating": 4.8}
    response = client.put("/api/v1/hotels/1", json=payload)
    assert response.status_code == 200
    hotel = response.json()
    assert hotel["name"] == "Grand Hyderabad Hotel Deluxe"
    assert hotel["rating"] == 4.8


def test_delete_hotel() -> None:
    response = client.delete("/api/v1/hotels/2")
    assert response.status_code == 204
    assert client.get("/api/v1/hotels/2").status_code == 404
    assert len(client.get("/api/v1/hotels").json()) == 1


def test_hotel_not_found() -> None:
    response = client.get("/api/v1/hotels/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Hotel not found."


def test_health_and_ready() -> None:
    health = client.get("/health")
    ready = client.get("/ready")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy", "service": "hotel-service"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready", "service": "hotel-service"}


def test_invalid_request() -> None:
    response = client.post("/api/v1/hotels", json={"name": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request."


def test_update_hotel_not_found() -> None:
    payload = {"name": "Missing Hotel", "city": "Goa", "rating": 4.0}
    response = client.put("/api/v1/hotels/999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Hotel not found."


def test_delete_hotel_not_found() -> None:
    response = client.delete("/api/v1/hotels/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Hotel not found."


def test_create_hotel_invalid_rating() -> None:
    payload = {"name": "Too High", "city": "Pune", "rating": 9.5}
    response = client.post("/api/v1/hotels", json=payload)
    assert response.status_code == 400
