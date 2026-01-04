from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime, date as dt_date
from enum import Enum

class BillType(str, Enum):
    electricity = "electricity"
    water = "water"

class User(Document):
    username: str = Field(index=True, unique=True)
    email: Optional[EmailStr] = None
    hashed_password: str
    language_pref: Optional[str] = "en"
    
    class Settings:
        name = "users"

class Bill(Document):
    user_id: str  # Reference to User document ID
    bill_type: str = "electricity"  # 'electricity' or 'water'
    image_path: str
    units_consumed: float
    total_amount: float
    bill_date: Optional[dt_date] = None
    is_verified: bool = True
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "bills"

class Appliance(Document):
    user_id: str  # Reference to User document ID
    name: str
    power_rating: float  # in watts
    avg_hours_per_day: float
    
    class Settings:
        name = "appliances"

class WeatherData(Document):
    record_date: dt_date = Field(index=True, unique=True)
    temperature: float
    humidity: float
    rainfall: float
    
    class Settings:
        name = "weather_data"
