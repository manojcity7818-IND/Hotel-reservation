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


def test_pay_with_net_banking() -> None:
    payload = {
        "booking_id": 4,
        "amount": 3200,
        "method": "NET_BANKING",
        "payer_name": "Aryan Kumar",
        "bank_name": "HDFC",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["reference"] == "HDFC"


def test_pay_with_wallet() -> None:
    payload = {
        "booking_id": 5,
        "amount": 2100,
        "method": "WALLET",
        "payer_name": "Aryan Kumar",
        "wallet_name": "Paytm",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    assert response.json()["reference"] == "Paytm"


def test_failed_upi_payment() -> None:
    payload = {
        "booking_id": 6,
        "amount": 1500,
        "method": "UPI",
        "payer_name": "Aryan Kumar",
        "upi_id": "guest@fail",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "FAILED"


def test_card_requires_number() -> None:
    payload = {
        "booking_id": 7,
        "amount": 1000,
        "method": "CARD",
        "payer_name": "Aryan",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 400
    assert "Card number" in response.json()["detail"]


def test_short_card_reference() -> None:
    payload = {
        "booking_id": 8,
        "amount": 1000,
        "method": "CARD",
        "payer_name": "Aryan",
        "card_number": "12",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 201
    assert response.json()["reference"] == "card-****XXXX"


def test_net_banking_default_reference() -> None:
    payload = {
        "booking_id": 9,
        "amount": 1000,
        "method": "NET_BANKING",
        "payer_name": "Aryan",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.json()["reference"] == "net-banking"


def test_wallet_default_reference() -> None:
    payload = {
        "booking_id": 10,
        "amount": 1000,
        "method": "WALLET",
        "payer_name": "Aryan",
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.json()["reference"] == "wallet"


def test_list_and_get_payment() -> None:
    created = client.post(
        "/api/v1/payments",
        json={
            "booking_id": 11,
            "amount": 4000,
            "method": "UPI",
            "payer_name": "Aryan",
            "upi_id": "aryan@ok",
        },
    ).json()
    listed = client.get("/api/v1/payments")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    fetched = client.get(f"/api/v1/payments/{created['payment_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["booking_id"] == 11


def test_invalid_amount() -> None:
    payload = {
        "booking_id": 1,
        "amount": 0,
        "method": "UPI",
        "payer_name": "Aryan",
        "upi_id": "a@upi",
    }
    assert client.post("/api/v1/payments", json=payload).status_code == 400


def test_invalid_method() -> None:
    payload = {
        "booking_id": 1,
        "amount": 100,
        "method": "CASH",
        "payer_name": "Aryan",
    }
    assert client.post("/api/v1/payments", json=payload).status_code == 400


def test_unhandled_error_returns_500() -> None:
    from unittest.mock import patch

    with patch("app.main.data.next_id", side_effect=RuntimeError("boom")):
        response = client.post(
            "/api/v1/payments",
            json={
                "booking_id": 1,
                "amount": 100,
                "method": "WALLET",
                "payer_name": "Aryan",
            },
        )
    assert response.status_code == 500
