from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SupportBase(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)

class SupportCreate(SupportBase):
    pass

class SupportUpdate(BaseModel):
    status: Optional[str] = Field(None, min_length=1, max_length=50)

class SupportResponse(SupportBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True