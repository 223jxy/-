from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.utils.database import Base

class Charity(Base):
    __tablename__ = "charities"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    book_title = Column(String(200))
    quantity = Column(Integer, default=1)
    destination = Column(String(200))  # 捐赠目的地
    status = Column(String(100), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    volunteer_hours = Column(Integer, default=0)  # 志愿时长

    # 关系
    donor = relationship("User", back_populates="charities")