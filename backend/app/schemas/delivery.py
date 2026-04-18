from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.delivery import DeliveryStatus

class DeliveryBase(BaseModel):
    order_id: int
    pickup_location: str = Field(..., min_length=1, max_length=200)
    delivery_location: str = Field(..., min_length=1, max_length=200)
    fee: int = Field(..., ge=0)
    reward: int = Field(..., ge=0)
    is_express: bool = False

class DeliveryCreate(DeliveryBase):
    pass

class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    delivery_person_id: Optional[int] = None
    status: DeliveryStatus
    pickup_location: str
    delivery_location: str
    estimated_time: datetime
    created_at: datetime
    updated_at: datetime
    fee: int
    reward: int
    rating: Optional[int] = None

    class Config:
        orm_mode = True