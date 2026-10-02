from pydantic import BaseModel
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None
    is_active: bool | None = None