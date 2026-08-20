from datetime import date
from enum import Enum

from pydantic import BaseModel


class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Booking(BaseModel):
    booking_id: int
    hotel_id: int
    room_id: int
    customer_name: str
    customer_email: str
    check_in: date
    check_out: date
    status: BookingStatus
