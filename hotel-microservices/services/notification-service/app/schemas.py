from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class NotificationEvent(str, Enum):
    BOOKING_CREATED = "BOOKING_CREATED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class NotificationCreate(BaseModel):
    booking_id: int
    event: NotificationEvent
    channel: NotificationChannel = NotificationChannel.EMAIL
    recipient: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class NotificationResponse(BaseModel):
    notification_id: int
    booking_id: int
    event: NotificationEvent
    channel: NotificationChannel
    recipient: str
    subject: str
    message: str
    status: str
    error: Optional[str] = None
