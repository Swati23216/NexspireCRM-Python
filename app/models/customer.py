from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field


class Customer(Document):

    # Application-level customer ID
    customer_id: int

    # Customer information
    name: str
    email: str
    phone: str

    company: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None

    # User who created this customer
    created_by: Optional[int] = None

    # Customer status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "customers"

