from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app import room_client


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
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

    def post(self, path: str) -> _FakeResponse:
        return self._response


def test_get_availability_true() -> None:
    response = _FakeResponse(200, {"room_id": 101, "available": True})
    with patch.object(room_client, "_client", return_value=_FakeClient(response)):
        assert room_client.get_availability(101) is True


def test_get_availability_room_not_found() -> None:
    response = _FakeResponse(404)
    with patch.object(room_client, "_client", return_value=_FakeClient(response)):
        with pytest.raises(HTTPException) as exc:
            room_client.get_availability(999)
    assert exc.value.status_code == 404


def test_get_availability_service_down() -> None:
    fake = MagicMock()
    fake.__enter__.side_effect = httpx.ConnectError("boom")
    with patch.object(room_client, "_client", return_value=fake):
        with pytest.raises(room_client.RoomServiceError):
            room_client.get_availability(101)


def test_reserve_conflict() -> None:
    response = _FakeResponse(409)
    with patch.object(room_client, "_client", return_value=_FakeClient(response)):
        with pytest.raises(HTTPException) as exc:
            room_client.reserve_room(101)
    assert exc.value.status_code == 409
    assert "unavailable" in exc.value.detail


def test_release_already_available_is_ok() -> None:
    response = _FakeResponse(409)
    with patch.object(room_client, "_client", return_value=_FakeClient(response)):
        room_client.release_room(101)


def test_reserve_server_error() -> None:
    response = _FakeResponse(500)
    with patch.object(room_client, "_client", return_value=_FakeClient(response)):
        with pytest.raises(room_client.RoomServiceError):
            room_client.reserve_room(101)
