from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field

class Lead(Document):
    lead_id: int = Field(..., description="Unique identifier for the lead")
    name: str = Field(..., description="Name of the lead")
    email: str = Field(..., description="Email address of the lead")
    phone: str = Field(..., description="Phone number of the lead")
    company: str = Field(..., description="Company of the lead")
    source: str = Field(..., description="Source of the lead")
    status: str = Field(..., description="Status of the lead")
    assigned_to: int | None = Field(None, description="ID of the user to whom the lead is assigned")
    service_interest: Optional[str] = None
    message: Optional[str] = None

    is_active: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "leads"