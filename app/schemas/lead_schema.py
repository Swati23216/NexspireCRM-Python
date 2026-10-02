from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LeadCreate(BaseModel):
    lead_id: Optional[int] = None
    name: str
    email: str
    phone: str
    company: str
    source: str


class PublicInquiry(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=32)
    company: str = Field(min_length=2, max_length=160)
    service_interest: str = Field(min_length=2, max_length=120)
    message: str = Field(min_length=10, max_length=2000)
    website: str = ""


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None

class LeadDelete(BaseModel):
    lead_id: int

class AssignLead(BaseModel):
    user_id: int
    