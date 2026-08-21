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
    names = {hotel["name"] for hotel in hotels}
    cities = {hotel["city"] for hotel in hotels}
    assert len(hotels) >= 250
    assert "Grand Hyderabad Hotel" in names
    assert "Bangalore Palace Hotel" in names
    assert "Mysore Palace View Hotel" in names
    assert "Lake Pichola Palace Hotel" in names
    assert {
        "Hyderabad",
        "Bangalore",
        "Mumbai",
        "New Delhi",
        "Chennai",
        "Goa",
        "Mysore",
        "Udaipur",
    }.issubset(cities)
    hyderabad = [hotel for hotel in hotels if hotel["city"] == "Hyderabad"]
    assert 20 <= len(hyderabad) <= 30


def test_filter_hotels_by_city() -> None:
    response = client.get("/api/v1/hotels", params={"q": "Mumbai"})
    assert response.status_code == 200
    hotels = response.json()
    assert 20 <= len(hotels) <= 30
    assert all("mumbai" in hotel["city"].lower() or "mumbai" in hotel["name"].lower() for hotel in hotels)


def test_get_hotel_by_id() -> None:
    response = client.get("/api/v1/hotels/1")
    assert response.status_code == 200
    hotel = response.json()
    assert hotel["id"] == 1
    assert hotel["city"] == "Hyderabad"


def test_create_hotel() -> None:
    existing = client.get("/api/v1/hotels").json()
    payload = {"name": "Mysore Garden Hotel", "city": "Mysore", "rating": 4.0}
    response = client.post("/api/v1/hotels", json=payload)
    assert response.status_code == 201
    hotel = response.json()
    assert hotel["id"] == max(item["id"] for item in existing) + 1
    assert hotel["name"] == "Mysore Garden Hotel"


def test_update_hotel() -> None:
    payload = {"name": "Grand Hyderabad Hotel Deluxe", "city": "Hyderabad", "rating": 4.8}
    response = client.put("/api/v1/hotels/1", json=payload)
    assert response.status_code == 200
    hotel = response.json()
    assert hotel["name"] == "Grand Hyderabad Hotel Deluxe"
    assert hotel["rating"] == 4.8


def test_delete_hotel() -> None:
    before = len(client.get("/api/v1/hotels").json())
    response = client.delete("/api/v1/hotels/2")
    assert response.status_code == 204
    assert client.get("/api/v1/hotels/2").status_code == 404
    assert len(client.get("/api/v1/hotels").json()) == before - 1


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


def test_filter_hotels_by_city_param() -> None:
    response = client.get("/api/v1/hotels", params={"city": "Udaipur"})
    hotels = response.json()
    assert len(hotels) == 10
    assert all(hotel["city"] == "Udaipur" for hotel in hotels)


def test_filter_hotels_by_name() -> None:
    response = client.get("/api/v1/hotels", params={"q": "Grand Hyderabad"})
    hotels = response.json()
    assert any(hotel["name"] == "Grand Hyderabad Hotel" for hotel in hotels)


def test_filter_hotels_no_match() -> None:
    response = client.get("/api/v1/hotels", params={"q": "Atlantis"})
    assert response.status_code == 200
    assert response.json() == []


def test_catalog_has_twelve_cities_and_270_hotels() -> None:
    hotels = client.get("/api/v1/hotels").json()
    cities = {hotel["city"] for hotel in hotels}
    assert len(hotels) == 270
    assert cities == {
        "Hyderabad",
        "Bangalore",
        "Mumbai",
        "New Delhi",
        "Chennai",
        "Goa",
        "Jaipur",
        "Pune",
        "Kolkata",
        "Kochi",
        "Mysore",
        "Udaipur",
    }


def test_mysore_and_kochi_counts() -> None:
    hotels = client.get("/api/v1/hotels").json()
    by_city = {}
    for hotel in hotels:
        by_city.setdefault(hotel["city"], 0)
        by_city[hotel["city"]] += 1
    assert by_city["Mysore"] == 10
    assert by_city["Kochi"] == 25


def test_unhandled_error_returns_500() -> None:
    from unittest.mock import patch

    with patch("app.main.data.next_id", side_effect=RuntimeError("boom")):
        response = client.post(
            "/api/v1/hotels",
            json={"name": "Crash Hotel", "city": "Goa", "rating": 4.0},
        )
    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected internal error."
