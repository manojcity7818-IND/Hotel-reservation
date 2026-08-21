from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import data
from app.emailer import EmailDeliveryError, send_email
from app.models import Notification
from app.schemas import NotificationCreate, NotificationResponse

app = FastAPI(title="Notification Service", version="1.0.0")
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500, content={"detail": "Unexpected internal error."}
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "notification-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "notification-service"}


@app.post("/api/v1/notifications", response_model=NotificationResponse, status_code=201)
def create_notification(payload: NotificationCreate) -> Notification:
    status = "SENT"
    error = None
    if payload.channel.value == "EMAIL":
        try:
            send_email(payload.recipient, payload.subject, payload.message)
        except EmailDeliveryError as exc:
            status = "FAILED"
            error = str(exc)
    notification = Notification(
        notification_id=data.next_id(),
        booking_id=payload.booking_id,
        event=payload.event,
        channel=payload.channel,
        recipient=payload.recipient,
        subject=payload.subject,
        message=payload.message,
        status=status,
        error=error,
    )
    data.notifications[notification.notification_id] = notification
    return notification


@app.get("/api/v1/notifications", response_model=list[NotificationResponse])
def list_notifications(booking_id: Optional[int] = None) -> list[Notification]:
    items = list(data.notifications.values())
    if booking_id is None:
        return items
    return [item for item in items if item.booking_id == booking_id]


@app.get("/api/v1/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int) -> Notification:
    notification = data.notifications.get(notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return notification
