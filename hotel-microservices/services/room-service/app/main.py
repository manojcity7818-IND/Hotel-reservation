from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import data
from app.models import Room
from app.schemas import AvailabilityResponse, RoomCreate, RoomResponse, RoomUpdate

app = FastAPI(title="Room Service", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": "Invalid request."})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500, content={"detail": "Unexpected internal error."}
    )


def _get_room_or_404(room_id: int) -> Room:
    room = data.rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")
    return room


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "room-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "room-service"}


@app.get("/api/v1/rooms", response_model=list[RoomResponse])
def get_rooms() -> list[Room]:
    return list(data.rooms.values())


@app.get("/api/v1/rooms/hotel/{hotel_id}", response_model=list[RoomResponse])
def get_rooms_by_hotel(hotel_id: int) -> list[Room]:
    return [room for room in data.rooms.values() if room.hotel_id == hotel_id]


@app.get("/api/v1/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: int) -> Room:
    return _get_room_or_404(room_id)


@app.post("/api/v1/rooms", response_model=RoomResponse, status_code=201)
def create_room(payload: RoomCreate) -> Room:
    room = Room(id=data.next_id(), **payload.model_dump())
    data.rooms[room.id] = room
    return room


@app.put("/api/v1/rooms/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, payload: RoomUpdate) -> Room:
    _get_room_or_404(room_id)
    room = Room(id=room_id, **payload.model_dump())
    data.rooms[room_id] = room
    return room


@app.delete("/api/v1/rooms/{room_id}", status_code=204)
def delete_room(room_id: int) -> None:
    _get_room_or_404(room_id)
    del data.rooms[room_id]


@app.get("/api/v1/rooms/{room_id}/availability", response_model=AvailabilityResponse)
def get_availability(room_id: int) -> AvailabilityResponse:
    room = _get_room_or_404(room_id)
    return AvailabilityResponse(room_id=room.id, available=room.available)


@app.post("/api/v1/rooms/{room_id}/reserve", response_model=RoomResponse)
def reserve_room(room_id: int) -> Room:
    room = _get_room_or_404(room_id)
    if not room.available:
        raise HTTPException(status_code=409, detail="Room is already reserved.")
    room.available = False
    return room


@app.post("/api/v1/rooms/{room_id}/release", response_model=RoomResponse)
def release_room(room_id: int) -> Room:
    room = _get_room_or_404(room_id)
    if room.available:
        raise HTTPException(status_code=409, detail="Room is not currently reserved.")
    room.available = True
    return room
