from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, model_validator


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class BookingCreate(BaseModel):
    hotel_id: int
    room_id: int
    customer_name: str = Field(..., min_length=1)
    customer_email: EmailStr
    check_in: date
    check_out: date
    amount: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingCreate":
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class BookingPaymentComplete(BaseModel):
    payment_id: int


class BookingResponse(BaseModel):
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
