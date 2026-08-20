from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import data
from app.models import Payment, PaymentMethod, PaymentStatus
from app.schemas import PaymentCreate, PaymentMethodInfo, PaymentResponse

app = FastAPI(title="Payment Service", version="1.0.0")
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


def _should_fail(payload: PaymentCreate) -> bool:
    if payload.method == PaymentMethod.UPI and (payload.upi_id or "").endswith("@fail"):
        return True
    if payload.method == PaymentMethod.CARD and (payload.card_number or "").startswith("0000"):
        return True
    return False


def _reference(payload: PaymentCreate, payment_id: int) -> str:
    if payload.method == PaymentMethod.UPI:
        return payload.upi_id or f"upi-{payment_id}"
    if payload.method == PaymentMethod.CARD:
        digits = "".join(ch for ch in (payload.card_number or "") if ch.isdigit())
        last4 = digits[-4:] if len(digits) >= 4 else "XXXX"
        return f"card-****{last4}"
    if payload.method == PaymentMethod.NET_BANKING:
        return payload.bank_name or "net-banking"
    return payload.wallet_name or "wallet"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "payment-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "payment-service"}


@app.get("/api/v1/payments/methods", response_model=list[PaymentMethodInfo])
def list_methods() -> list[PaymentMethodInfo]:
    return [
        PaymentMethodInfo(
            method=PaymentMethod.UPI,
            label="UPI",
            description="Pay with GPay, PhonePe, Paytm or any UPI ID",
        ),
        PaymentMethodInfo(
            method=PaymentMethod.CARD,
            label="Credit / Debit card",
            description="Visa, Mastercard, RuPay and Amex",
        ),
        PaymentMethodInfo(
            method=PaymentMethod.NET_BANKING,
            label="Net banking",
            description="Pay directly from your bank account",
        ),
        PaymentMethodInfo(
            method=PaymentMethod.WALLET,
            label="Wallet",
            description="Paytm, Amazon Pay and other wallets",
        ),
    ]


@app.post("/api/v1/payments", response_model=PaymentResponse, status_code=201)
def create_payment(payload: PaymentCreate) -> Payment:
    if payload.method == PaymentMethod.UPI and not payload.upi_id:
        raise HTTPException(status_code=400, detail="UPI ID is required.")
    if payload.method == PaymentMethod.CARD and not payload.card_number:
        raise HTTPException(status_code=400, detail="Card number is required.")

    payment_id = data.next_id()
    status = PaymentStatus.FAILED if _should_fail(payload) else PaymentStatus.SUCCESS
    payment = Payment(
        payment_id=payment_id,
        booking_id=payload.booking_id,
        amount=payload.amount,
        method=payload.method,
        status=status,
        payer_name=payload.payer_name,
        reference=_reference(payload, payment_id),
    )
    data.payments[payment_id] = payment
    return payment


@app.get("/api/v1/payments", response_model=list[PaymentResponse])
def list_payments() -> list[Payment]:
    return list(data.payments.values())


@app.get("/api/v1/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int) -> Payment:
    payment = data.payments.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return payment
