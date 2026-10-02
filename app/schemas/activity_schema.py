from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActivityCreate(BaseModel):

    subject: str

    activity_type: str = "Task"

    description: Optional[str] = None

    customer_id: Optional[int] = None

    lead_id: Optional[int] = None

    opportunity_id: Optional[int] = None

    due_date: Optional[datetime] = None

    status: str = "Pending"

    assigned_to: Optional[int] = None


class ActivityUpdate(BaseModel):

    subject: Optional[str] = None

    activity_type: Optional[str] = None

    description: Optional[str] = None

    customer_id: Optional[int] = None

    lead_id: Optional[int] = None

    opportunity_id: Optional[int] = None

    due_date: Optional[datetime] = None

    status: Optional[str] = None

    assigned_to: Optional[int] = None

    is_active: Optional[bool] = None