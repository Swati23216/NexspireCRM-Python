from datetime import datetime

from beanie import Document
from pydantic import Field


class Opportunity(Document):

    opportunity_id: int

    name: str
    customer_id: int
    lead_id: int | None = None
    description: str | None = None

    amount: float = 0
    stage: str = "Prospecting"
    probability: float = 0

    expected_close_date: datetime | None = None
    assigned_to: int | None = None

    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "opportunities"