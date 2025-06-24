from typing import List, Optional
from pydantic import BaseModel, EmailStr,  field_validator, Field, ConfigDict
from datetime import datetime, time


# 1. User schema 
class UserBase(BaseModel):
    user_id: str
    email: EmailStr

class UserCreate(UserBase):
    password: str  # raw password, will be hashed 

class UserResponse(UserBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class config:
        from_attributes = True


# LogIn user
class LoginRequest(BaseModel):
    user_id: str
    password: str

    # Validation
    @classmethod
    def validate_input(cls, values):
        if not values.get("user_id"):
            raise ValueError("Either email or user_id is required.")
        return values
    
    model_config = ConfigDict(
        extra="forbid",   # disallow extra fields
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "email": "emailexample@examle.com",
                "password": "secure-password123"
            }
        }
    )    

class LoginResponse(BaseModel):
    access_token: str
    token_type: str