from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CartItem(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int = Field(gt=0)
    subtotal: float


class CartBase(BaseModel):
    items: List[CartItem] = []
    total_amount: float = 0.0


class CartAddItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, default=1)


class CartUpdateItem(BaseModel):
    product_id: str
    quantity: int = Field(ge=0)


class CartResponse(CartBase):
    id: str = Field(alias="_id")
    user_id: str
    updated_at: datetime
    
    class Config:
        populate_by_name = True
