from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import data, room_client
from app.models import Booking, BookingStatus
from app.room_client import RoomServiceError
from app.schemas import BookingCreate, BookingResponse

app = FastAPI(title="Booking Service", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": "Invalid request."})


@app.exception_handler(RoomServiceError)
async def room_service_error_handler(
    request: Request, exc: RoomServiceError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc) or "Room Service is unavailable."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500, content={"detail": "Unexpected internal error."}
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "booking-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "booking-service"}


@app.post("/api/v1/bookings", response_model=BookingResponse, status_code=201)
def create_booking(payload: BookingCreate) -> Booking:
    available = room_client.get_availability(payload.room_id)
    if not available:
        raise HTTPException(
            status_code=409,
            detail="Cannot create booking because room is unavailable.",
        )

    room_client.reserve_room(payload.room_id)

    booking = Booking(
        booking_id=data.next_id(),
        hotel_id=payload.hotel_id,
        room_id=payload.room_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        check_in=payload.check_in,
        check_out=payload.check_out,
        status=BookingStatus.CONFIRMED,
    )
    data.bookings[booking.booking_id] = booking
    return booking


@app.get("/api/v1/bookings", response_model=list[BookingResponse])
def get_bookings() -> list[Booking]:
    return list(data.bookings.values())


@app.get("/api/v1/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int) -> Booking:
    booking = data.bookings.get(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking


@app.delete("/api/v1/bookings/{booking_id}", response_model=BookingResponse)
def cancel_booking(booking_id: int) -> Booking:
    booking = data.bookings.get(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Booking is already cancelled.")

    room_client.release_room(booking.room_id)
    booking.status = BookingStatus.CANCELLED
    return booking
