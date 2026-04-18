from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.book import BookCondition

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=1, max_length=20)
    original_price: float = Field(..., gt=0)
    condition: BookCondition
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    university: str = Field(..., min_length=1, max_length=100)
    major: str = Field(..., min_length=1, max_length=100)
    grade: str = Field(..., min_length=1, max_length=50)

class BookCreate(BookBase):
    owner_id: int

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, min_length=1, max_length=20)
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    condition: Optional[BookCondition] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_sold: Optional[bool] = None
    is_rented: Optional[bool] = None

class BookResponse(BookBase):
    id: int
    price: float
    owner_id: int
    is_sold: bool
    is_rented: bool
    cover_image: Optional[str] = None

    class Config:
        orm_mode = True