from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.utils.database import Base

class DeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    delivery_person_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING)
    pickup_location = Column(String(200))
    delivery_location = Column(String(200))
    estimated_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fee = Column(Integer, default=0)
    reward = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)

    # 关系
    order = relationship("Order", back_populates="delivery")
    delivery_person = relationship("User", back_populates="deliveries")