from datetime import datetime

from pydantic import BaseModel


class OpportunityCreate(BaseModel):

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


class OpportunityUpdate(BaseModel):

    name: str | None = None

    customer_id: int | None = None

    lead_id: int | None = None

    description: str | None = None

    amount: float | None = None

    stage: str | None = None

    probability: float | None = None

    expected_close_date: datetime | None = None

    assigned_to: int | None = None

    is_active: bool | None = None