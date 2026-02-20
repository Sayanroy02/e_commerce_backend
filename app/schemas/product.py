from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    category: str
    stock_quantity: int = Field(ge=0)
    images: Optional[List[str]] = []
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
