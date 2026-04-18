from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CharityBase(BaseModel):
    book_id: Optional[int] = None
    book_title: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., ge=1)
    destination: str = Field(..., min_length=1, max_length=200)
    volunteer_hours: int = Field(..., ge=0)

class CharityCreate(CharityBase):
    pass

class CharityUpdate(BaseModel):
    status: Optional[str] = Field(None, min_length=1, max_length=100)
    volunteer_hours: Optional[int] = Field(None, ge=0)

class CharityResponse(CharityBase):
    id: int
    donor_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True