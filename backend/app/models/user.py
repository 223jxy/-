from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.utils.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    university = Column(String(100))
    major = Column(String(100))
    grade = Column(String(50))
    is_student = Column(Boolean, default=True)
    is_delivery = Column(Boolean, default=False)
    carbon_points = Column(Integer, default=0)

    # 关系
    books = relationship("Book", back_populates="owner")
    orders = relationship("Order", back_populates="user")
    carbon_point_records = relationship("CarbonPoint", back_populates="user")
    deliveries = relationship("Delivery", back_populates="delivery_person")
    charities = relationship("Charity", back_populates="donor")
    study_notes = relationship("StudyNote", back_populates="author")