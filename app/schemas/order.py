from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.schemas.user import Address


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    subtotal: float


class OrderCreate(BaseModel):
    shipping_address: Address
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    tracking_number: Optional[str] = None


class OrderResponse(BaseModel):
    id: str = Field(alias="_id")
    order_number: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_address: Address
    status: OrderStatus
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class OrderTracking(BaseModel):
    order_number: str
    status: OrderStatus
    tracking_number: Optional[str] = None
    status_history: List[dict] = []
    created_at: datetime
    updated_at: datetime
