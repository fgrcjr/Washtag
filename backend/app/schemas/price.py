from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class PriceBase(BaseModel):
    type: str = Field(..., min_length=1, max_length=100, description="Type of clothing or service")
    weight_min: Optional[float] = Field(None, gt=0, description="Minimum weight in kg (required for non-Custom types)")
    weight_max: float = Field(..., gt=0, description="Maximum weight in kg")
    amount: float = Field(..., gt=0, description="Price amount")
    category_id: int = Field(..., description="Category ID")

    @validator('weight_min')
    def weight_min_required_for_non_custom(cls, v, values):
        if 'type' in values and values['type'].lower() != 'custom' and v is None:
            raise ValueError('weight_min is required for non-Custom types')
        return v

    @validator('weight_max')
    def weight_max_must_be_greater_than_min(cls, v, values):
        if 'weight_min' in values and values['weight_min'] is not None and v <= values['weight_min']:
            raise ValueError('weight_max must be greater than weight_min')
        return v


class PriceCreate(PriceBase):
    pass


class PriceUpdate(BaseModel):
    type: Optional[str] = Field(None, min_length=1, max_length=100, description="Type of clothing or service")
    weight_min: Optional[float] = Field(None, gt=0, description="Minimum weight in kg (required for non-Custom types)")
    weight_max: Optional[float] = Field(None, gt=0, description="Maximum weight in kg")
    amount: Optional[float] = Field(None, gt=0, description="Price amount")
    category_id: Optional[int] = Field(None, description="Category ID")

    @validator('weight_min')
    def weight_min_required_for_non_custom(cls, v, values):
        if 'type' in values and values['type'] is not None and values['type'].lower() != 'custom' and v is None:
            raise ValueError('weight_min is required for non-Custom types')
        return v

    @validator('weight_max')
    def weight_max_must_be_greater_than_min(cls, v, values):
        if v is not None and 'weight_min' in values and values['weight_min'] is not None and v <= values['weight_min']:
            raise ValueError('weight_max must be greater than weight_min')
        return v


class PriceResponse(PriceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PriceWithCategory(PriceResponse):
    category: dict = Field(..., description="Category information")

    class Config:
        from_attributes = True
