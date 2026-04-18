from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.utils.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    DELIVERING = "DELIVERING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class OrderType(str, enum.Enum):
    SALE = "SALE"
    RENT = "RENT"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    book_id = Column(Integer, ForeignKey("books.id"), index=True)
    order_type = Column(SQLEnum(OrderType))
    price = Column(Float)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=True, index=True)

    # 关系
    user = relationship("User", back_populates="orders")
    book = relationship("Book", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order")