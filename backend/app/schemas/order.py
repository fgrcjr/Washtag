from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
import re

from app.schemas.client import ClientResponse
from app.schemas.category import CategoryResponse


class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderBase(BaseModel):
    client_id: int = Field(..., description="Client ID")
    category_id: int = Field(..., description="Category ID")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Order status")
    total_amount: Optional[float] = Field(None, ge=0, description="Total amount")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    client_id: Optional[int] = Field(None, description="Client ID")
    category_id: Optional[int] = Field(None, description="Category ID")
    status: Optional[OrderStatus] = Field(None, description="Order status")
    total_amount: Optional[float] = Field(None, ge=0, description="Total amount")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")


class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderResponseWithDetails(OrderResponse):
    client: ClientResponse
    category: CategoryResponse

    class Config:
        from_attributes = True


# Integrated Order Schemas for New Client Workflow
class IntegratedOrderCreate(BaseModel):
    """Schema for integrated order creation with automatic client handling"""
    
    # Client information (will create if not exists)
    client_name: str = Field(..., min_length=1, max_length=100, description="Client name")
    client_contact: str = Field(..., min_length=11, max_length=11, description="Client contact number (11 digits)")
    client_address: str = Field(..., min_length=1, max_length=255, description="Client address")
    
    # Order details
    category_id: int = Field(..., description="Category ID")
    type_name: str = Field(..., min_length=1, max_length=100, description="Type of clothing or service")
    weight: float = Field(..., gt=0, description="Weight in kg")
    
    # Custom pricing (only used when type_name is 'custom')
    custom_amount: Optional[float] = Field(None, gt=0, description="Custom amount (only for custom type)")
    
    # Optional order details
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Order status")
    
    @validator('client_contact')
    def validate_contact_number(cls, v):
        """Validate contact number format"""
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) != 11:
            raise ValueError('Contact number must be exactly 11 digits')
        if not digits_only.isdigit():
            raise ValueError('Contact number must contain only digits')
        return digits_only
    
    @validator('custom_amount')
    def validate_custom_amount(cls, v, values):
        """Validate custom amount is provided when type is custom"""
        if 'type_name' in values and values['type_name'].lower() == 'custom' and v is None:
            raise ValueError('custom_amount is required when type_name is "custom"')
        if 'type_name' in values and values['type_name'].lower() != 'custom' and v is not None:
            raise ValueError('custom_amount should only be provided when type_name is "custom"')
        return v


class IntegratedOrderResponse(BaseModel):
    """Response schema for integrated order creation"""
    
    # Order information
    order_id: int
    status: str
    total_amount: float
    notes: Optional[str]
    created_at: str
    
    # Client information
    client_id: int
    client_name: str
    client_contact: str
    client_address: str
    
    # Category information
    category_id: int
    category_name: str
    
    # Price information
    type_name: str
    weight: float
    price_id: Optional[int]  # None for custom pricing
    
    class Config:
        from_attributes = True