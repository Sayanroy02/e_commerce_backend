from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class Address(BaseModel):
    street: str
    city: str
    state: str
    country: str
    postal_code: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    role: UserRole = UserRole.CUSTOMER
    address: Optional[Address] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    id: str = Field(alias="_id")
    role: UserRole
    address: Optional[Address] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None
