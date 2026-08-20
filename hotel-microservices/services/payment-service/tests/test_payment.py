from fastapi.testclient import TestClient

from app import data
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def setup_function() -> None:
    data.reset_data()


def test_list_payment_methods() -> None:
    response = client.get("/api/v1/payments/methods")
    assert response.status_code == 200
    methods = {item["method"] for item in response.json()}
    assert methods == {"UPI", "CARD", "NET_BANKING", "WALLET"}


def test_pay_with_upi() -> None:
    payload = {
        "booking_id": 1,
        "amount": 10000,
        "method": "UPI",
        "payer_name": "Aryan Kumar",
        "upi_id": "aryan@upi",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["method"] == "UPI"
    assert body["reference"] == "aryan@upi"


def test_pay_with_card() -> None:
    payload = {
        "booking_id": 2,
        "amount": 7500,
        "method": "CARD",
        "payer_name": "Aryan Kumar",
        "card_number": "4111111111111111",
        "card_holder": "Aryan Kumar",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["reference"].endswith("1111")


def test_failed_card_payment() -> None:
    payload = {
        "booking_id": 3,
        "amount": 5000,
        "method": "CARD",
        "payer_name": "Aryan Kumar",
        "card_number": "0000111122223333",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "FAILED"


def test_payment_not_found() -> None:
    response = client.get("/api/v1/payments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found."


def test_upi_requires_id() -> None:
    payload = {
        "booking_id": 1,
        "amount": 1000,
        "method": "UPI",
        "payer_name": "Aryan",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 400


def test_health_and_ready() -> None:
    assert client.get("/health").json()["service"] == "payment-service"
    assert client.get("/ready").json()["status"] == "ready"
