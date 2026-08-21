from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import data, notification_client, payment_client, room_client
from app.models import Booking, BookingStatus
from app.payment_client import PaymentServiceError
from app.room_client import RoomServiceError
from app.schemas import BookingCreate, BookingPaymentComplete, BookingResponse

app = FastAPI(title="Booking Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.exception_handler(PaymentServiceError)
async def payment_service_error_handler(
    request: Request, exc: PaymentServiceError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc) or "Payment Service is unavailable."},
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
        status=BookingStatus.PENDING_PAYMENT,
        amount=payload.amount,
    )
    data.bookings[booking.booking_id] = booking
    notification_client.notify_booking(
        booking,
        "BOOKING_CREATED",
        "Aryanstays booking received",
        f"Hi {booking.customer_name}, booking #{booking.booking_id} is reserved. Complete payment to confirm.",
    )
    return booking


@app.post("/api/v1/bookings/{booking_id}/pay", response_model=BookingResponse)
def complete_payment(booking_id: int, payload: BookingPaymentComplete) -> Booking:
    booking = data.bookings.get(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Booking is already cancelled.")
    if booking.status == BookingStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail="Booking is already paid.")

    payment = payment_client.get_payment(payload.payment_id)
    if payment.get("booking_id") != booking.booking_id:
        raise HTTPException(status_code=409, detail="Payment does not match this booking.")
    if payment.get("status") != "SUCCESS":
        booking.status = BookingStatus.PAYMENT_FAILED
        notification_client.notify_booking(
            booking,
            "PAYMENT_FAILED",
            "Aryanstays payment failed",
            f"Hi {booking.customer_name}, payment for booking #{booking.booking_id} did not succeed.",
        )
        raise HTTPException(status_code=409, detail="Payment was not successful.")

    booking.payment_id = payload.payment_id
    booking.status = BookingStatus.CONFIRMED
    notification_client.notify_booking(
        booking,
        "BOOKING_CONFIRMED",
        "Aryanstays booking confirmed",
        f"Hi {booking.customer_name}, booking #{booking.booking_id} is confirmed.",
    )
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
    notification_client.notify_booking(
        booking,
        "BOOKING_CANCELLED",
        "Aryanstays booking cancelled",
        f"Hi {booking.customer_name}, booking #{booking.booking_id} was cancelled and the room was released.",
    )
    return booking
