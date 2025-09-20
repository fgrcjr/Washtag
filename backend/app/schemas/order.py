from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

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