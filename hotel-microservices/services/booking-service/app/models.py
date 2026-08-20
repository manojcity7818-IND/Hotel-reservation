from datetime import date
from enum import Enum

from pydantic import BaseModel


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class Booking(BaseModel):
    booking_id: int
    hotel_id: int
    room_id: int
    customer_name: str
    customer_email: str
    check_in: date
    check_out: date
    status: BookingStatus
    amount: float
    payment_id: int | None = None
