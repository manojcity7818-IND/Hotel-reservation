from typing import Optional
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app import payment_client


class _FakeResponse:
    def __init__(self, status_code: int, payload: Optional[dict] = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class _FakeClient:
    def __init__(self, response: _FakeResponse) -> None:
        self._response = response

    def __enter__(self) -> "_FakeClient":
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def get(self, path: str) -> _FakeResponse:
        return self._response


def test_get_payment_success() -> None:
    response = _FakeResponse(200, {"payment_id": 7, "status": "SUCCESS", "booking_id": 1})
    with patch.object(payment_client, "_client", return_value=_FakeClient(response)):
        body = payment_client.get_payment(7)
    assert body["status"] == "SUCCESS"


def test_get_payment_not_found() -> None:
    with patch.object(payment_client, "_client", return_value=_FakeClient(_FakeResponse(404))):
        with pytest.raises(HTTPException) as exc:
            payment_client.get_payment(99)
    assert exc.value.status_code == 404


def test_get_payment_server_error() -> None:
    with patch.object(payment_client, "_client", return_value=_FakeClient(_FakeResponse(500))):
        with pytest.raises(payment_client.PaymentServiceError):
            payment_client.get_payment(1)


def test_get_payment_unexpected_status() -> None:
    with patch.object(payment_client, "_client", return_value=_FakeClient(_FakeResponse(400))):
        with pytest.raises(HTTPException) as exc:
            payment_client.get_payment(1)
    assert exc.value.status_code == 502


def test_get_payment_unavailable() -> None:
    fake = MagicMock()
    fake.__enter__.side_effect = httpx.ConnectError("down")
    with patch.object(payment_client, "_client", return_value=fake):
        with pytest.raises(payment_client.PaymentServiceError):
            payment_client.get_payment(1)
