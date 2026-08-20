from enum import Enum

from pydantic import BaseModel


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(BaseModel):
    payment_id: int
    booking_id: int
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    payer_name: str
    reference: str
