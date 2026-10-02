from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class Ticket(Document):

    ticket_id: int = Field(
        ...,
        description="Unique Ticket ID"
    )

    subject: str

    description: Optional[str] = None

    # These are optional because your frontend
    # currently does not always send them.
    customer_id: Optional[int] = None

    priority: str = "Medium"

    status: str = "Open"

    category: Optional[str] = None

    assigned_to: Optional[int] = None

    is_active: bool = True

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    class Settings:
        name = "tickets"