import os

import httpx
from fastapi import HTTPException

ROOM_SERVICE_URL = os.getenv("ROOM_SERVICE_URL", "http://room-service:8000")
TIMEOUT_SECONDS = 5.0


class RoomServiceError(Exception):
    """Raised when Room Service cannot be reached."""


def _client() -> httpx.Client:
    return httpx.Client(base_url=ROOM_SERVICE_URL, timeout=TIMEOUT_SECONDS)


def get_availability(room_id: int) -> bool:
    try:
        with _client() as client:
            response = client.get(f"/api/v1/rooms/{room_id}/availability")
    except httpx.RequestError as exc:
        raise RoomServiceError("Room Service is unavailable.") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Room not found.")
    if response.status_code >= 500:
        raise RoomServiceError("Room Service returned an error.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected response from Room Service.")
    return bool(response.json().get("available"))


def reserve_room(room_id: int) -> None:
    try:
        with _client() as client:
            response = client.post(f"/api/v1/rooms/{room_id}/reserve")
    except httpx.RequestError as exc:
        raise RoomServiceError("Room Service is unavailable.") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Room not found.")
    if response.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail="Cannot create booking because room is unavailable.",
        )
    if response.status_code >= 500:
        raise RoomServiceError("Room Service returned an error.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected response from Room Service.")


def release_room(room_id: int) -> None:
    try:
        with _client() as client:
            response = client.post(f"/api/v1/rooms/{room_id}/release")
    except httpx.RequestError as exc:
        raise RoomServiceError("Room Service is unavailable.") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Room not found.")
    if response.status_code == 409:
        # Already available — treat as released for cancel idempotency.
        return
    if response.status_code >= 500:
        raise RoomServiceError("Room Service returned an error.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected response from Room Service.")
