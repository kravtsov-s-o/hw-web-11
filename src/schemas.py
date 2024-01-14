from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50, unique=True)
    last_name: str = Field(max_length=50, unique=True)
    email: str = Field(max_length=255, unique=True)
    phone: str = Field(max_length=20)
    birthday: date = Field()
    notes: Optional[str] = Field(None, max_length=512)


class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        # orm_mode = True
        from_attributes = True
