from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import LeadState

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    resume_path: str
    state: LeadState
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    state: Optional[LeadState] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedLeads(BaseModel):
    items: List[Lead]
    total: int
    has_more: bool
    last_id: Optional[int] = None

    class Config:
        from_attributes = True 