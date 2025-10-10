from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal
from datetime import datetime, timezone

class CreateUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, example='john', description='Username must be between 3 and 20 characters.')
    email: EmailStr = Field(...)
    first_name: str = Field(..., min_length=2, max_length=30)
    last_name: str = Field(..., min_length=2, max_length=30)
    phone_number: str
    password: str = Field(min_length=6, max_length=72, example='strongPassword123!', description='Password must be between 6 and 72 characters long.')
    admin: bool = False
    @field_validator('password')
    def validate_password(cls, value):
        if ' ' in value:
            raise ValueError('Password must not contain spaces.')
        if not any (char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not any (char.islower() for char in value):
            raise ValueError('Passowrd must contain at least one lowercase letter.')
        if not any (char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit number')
        return value
        
class CreateReservation(BaseModel):
    user_id: int
    reservation_time: datetime
    number_of_people: int

    @field_validator('reservation_time')
    def validate_reservation_time(cls, value):
        if value < datetime.now(timezone.utc):
            raise ValueError('Reservation time cannot be in the past.')
        return value

class Token(BaseModel):
    access_token: str
    token_type: str