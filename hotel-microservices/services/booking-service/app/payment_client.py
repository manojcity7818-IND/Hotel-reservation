import os

import httpx
from fastapi import HTTPException

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
TIMEOUT_SECONDS = 5.0


class PaymentServiceError(Exception):
    """Raised when Payment Service cannot be reached."""


def _client() -> httpx.Client:
    return httpx.Client(base_url=PAYMENT_SERVICE_URL, timeout=TIMEOUT_SECONDS)


def get_payment(payment_id: int) -> dict:
    try:
        with _client() as client:
            response = client.get(f"/api/v1/payments/{payment_id}")
    except httpx.RequestError as exc:
        raise PaymentServiceError("Payment Service is unavailable.") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Payment not found.")
    if response.status_code >= 500:
        raise PaymentServiceError("Payment Service returned an error.")
    if response.status_code != 200:
        raise HTTPException(
            status_code=502, detail="Unexpected response from Payment Service."
        )
    return response.json()
