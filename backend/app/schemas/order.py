from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus, OrderType

class OrderBase(BaseModel):
    book_id: int
    order_type: OrderType
    price: float = Field(..., gt=0)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    delivery_id: Optional[int] = None

    class Config:
        orm_mode = True