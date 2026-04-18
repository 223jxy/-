from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudyNoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)

class StudyNoteCreate(StudyNoteBase):
    pass

class StudyNoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, ge=0)

class StudyNoteResponse(StudyNoteBase):
    id: int
    author_id: int
    views: int
    likes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True