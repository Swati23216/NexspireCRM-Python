from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class Activity(Document):

    activity_id: int

    subject: str

    activity_type: str = "Task"

    description: Optional[str] = None

    customer_id: Optional[int] = None

    lead_id: Optional[int] = None

    opportunity_id: Optional[int] = None

    due_date: Optional[datetime] = None

    status: str = "Pending"

    assigned_to: Optional[int] = None

    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "activities"