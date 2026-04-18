from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CarbonPointBase(BaseModel):
    points: int = Field(..., gt=0)
    source: str = Field(..., min_length=1, max_length=100)

class CarbonPointCreate(CarbonPointBase):
    pass

class CarbonPointResponse(CarbonPointBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True