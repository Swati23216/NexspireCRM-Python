from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =========================================================
# CREATE FOLLOW-UP
# =========================================================

class FollowUpCreate(BaseModel):

    # Either lead_id OR ticket_id should be provided
    lead_id: Optional[int] = None

    ticket_id: Optional[int] = None

    subject: Optional[str] = None

    notes: Optional[str] = None

    remarks: Optional[str] = None

    next_followup_date: datetime


# =========================================================
# UPDATE FOLLOW-UP
# =========================================================

class FollowUpUpdate(BaseModel):

    lead_id: Optional[int] = None

    ticket_id: Optional[int] = None

    subject: Optional[str] = None

    notes: Optional[str] = None

    remarks: Optional[str] = None

    next_followup_date: Optional[datetime] = None
