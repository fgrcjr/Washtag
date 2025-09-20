from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Client name")
    contact_number: str = Field(..., min_length=11, max_length=11, description="Client contact number (11 digits)")
    address: str = Field(..., min_length=1, max_length=255, description="Client address")
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) != 11:
            raise ValueError('Contact number must be exactly 11 digits')
        if not digits_only.isdigit():
            raise ValueError('Contact number must contain only digits')
        return digits_only


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Client name")
    contact_number: Optional[str] = Field(None, min_length=11, max_length=11, description="Client contact number (11 digits)")
    address: Optional[str] = Field(None, min_length=1, max_length=255, description="Client address")
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        if v is None:
            return v
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) != 11:
            raise ValueError('Contact number must be exactly 11 digits')
        if not digits_only.isdigit():
            raise ValueError('Contact number must contain only digits')
        return digits_only


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
