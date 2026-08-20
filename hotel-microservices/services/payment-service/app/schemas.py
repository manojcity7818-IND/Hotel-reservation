from enum import Enum

from pydantic import BaseModel, Field


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentCreate(BaseModel):
    booking_id: int
    amount: float = Field(..., gt=0)
    method: PaymentMethod
    payer_name: str = Field(..., min_length=1)
    upi_id: str | None = None
    card_number: str | None = None
    card_holder: str | None = None
    bank_name: str | None = None
    wallet_name: str | None = None


class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: int
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    payer_name: str
    reference: str


class PaymentMethodInfo(BaseModel):
    method: PaymentMethod
    label: str
    description: str
