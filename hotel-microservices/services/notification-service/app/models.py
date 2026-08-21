from enum import Enum

from pydantic import BaseModel


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class NotificationEvent(str, Enum):
    BOOKING_CREATED = "BOOKING_CREATED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class Notification(BaseModel):
    notification_id: int
    booking_id: int
    event: NotificationEvent
    channel: NotificationChannel
    recipient: str
    subject: str
    message: str
    status: str = "SENT"
    error: str | None = None
