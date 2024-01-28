from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


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
        from_attributes = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = 'User was created.'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr
