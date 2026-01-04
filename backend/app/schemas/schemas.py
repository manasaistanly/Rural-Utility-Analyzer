from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    language_pref: Optional[str] = "en"

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr] = None
    language_pref: Optional[str] = "en"

    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Bill Schemas
class BillCreate(BaseModel):
    bill_type: str = "electricity"

class BillResponse(BaseModel):
    id: str
    user_id: str
    bill_type: str
    image_path: str
    units_consumed: float
    total_amount: float
    bill_date: Optional[date] = None
    is_verified: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True
