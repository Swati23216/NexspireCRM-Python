from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional


# =========================================================
# FOLLOW-UP DOCUMENT
# =========================================================

class FollowUp(Document):

    followup_id: Optional[int] = None

    # Follow-up can belong to a lead or ticket
    lead_id: Optional[int] = None
    ticket_id: Optional[int] = None

    subject: Optional[str] = None

    notes: Optional[str] = None

    remarks: str

    next_followup_date: datetime

    created_by: int

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "followups"


# =========================================================
# CREATE FOLLOW-UP
# =========================================================

class FollowUpCreate(BaseModel):

    lead_id: Optional[int] = None
    ticket_id: Optional[int] = None

    remarks: str

    next_followup_date: datetime


# =========================================================
# UPDATE FOLLOW-UP
# =========================================================

class FollowUpUpdate(BaseModel):

    lead_id: Optional[int] = None
    ticket_id: Optional[int] = None

    remarks: Optional[str] = None

    next_followup_date: Optional[datetime] = None
