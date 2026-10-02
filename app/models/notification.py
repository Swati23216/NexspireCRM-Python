
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


# ============================================================
# NOTIFICATION DOCUMENT
# ============================================================

class Notification(Document):

    notification_id: int

    user_id: int
    title: str
    message: str

    notification_type: str = "General"

    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    activity_id: Optional[int] = None
    ticket_id: Optional[int] = None

    is_read: bool = False
    is_active: bool = True

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "notifications"


# ============================================================
# CREATE NOTIFICATION
# ============================================================

class NotificationCreate(BaseModel):

    user_id: int
    title: str
    message: str

    notification_type: str = "General"

    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    activity_id: Optional[int] = None
    ticket_id: Optional[int] = None


# ============================================================
# UPDATE NOTIFICATION
# ============================================================

class NotificationUpdate(BaseModel):

    title: Optional[str] = None
    message: Optional[str] = None
    notification_type: Optional[str] = None

    is_read: Optional[bool] = None
    is_active: Optional[bool] = None

