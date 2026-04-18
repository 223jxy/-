from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
import enum

from app.utils.database import Base

class BookCondition(str, enum.Enum):
    A1 = "A1"  # 九成新
    A2 = "A2"  # 八五新
    B = "B"    # 八成新
    C = "C"    # 五成新以上

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    author = Column(String(100))
    isbn = Column(String(20), index=True)
    price = Column(Float)
    original_price = Column(Float)
    condition = Column(SQLEnum(BookCondition))
    category = Column(String(100))
    description = Column(String(500))
    university = Column(String(100), index=True)
    major = Column(String(100), index=True)
    grade = Column(String(50), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_sold = Column(Boolean, default=False, index=True)
    is_rented = Column(Boolean, default=False, index=True)

    # 关系
    owner = relationship("User", back_populates="books")
    orders = relationship("Order", back_populates="book")