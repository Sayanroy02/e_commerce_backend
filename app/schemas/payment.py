from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    RAZORPAY = "razorpay"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    CASH_ON_DELIVERY = "cash_on_delivery"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentCreate(BaseModel):
    order_id: str
    payment_method: PaymentMethod
    amount: float = Field(gt=0)


class RazorpayOrderCreate(BaseModel):
    order_id: str
    amount: float = Field(gt=0)
    currency: str = "INR"


class RazorpayOrderResponse(BaseModel):
    razorpay_order_id: str
    order_id: str
    amount: float
    currency: str
    status: str


class RazorpayPaymentVerify(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    id: str = Field(alias="_id")
    order_id: str
    user_id: str
    payment_method: PaymentMethod
    amount: float
    status: PaymentStatus
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
