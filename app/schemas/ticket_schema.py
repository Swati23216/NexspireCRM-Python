from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# CREATE TICKET
# ============================================================

class TicketCreate(BaseModel):

    title: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    priority: str = Field(
        default="Medium"
    )

    description: Optional[str] = None

    status: str = Field(
        default="Open"
    )

    customer_id: Optional[int] = None

    category: Optional[str] = None

    assigned_to: Optional[int] = None


# ============================================================
# UPDATE TICKET
# ============================================================

class TicketUpdate(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    priority: Optional[str] = None

    description: Optional[str] = None

    status: Optional[str] = None

    customer_id: Optional[int] = None

    category: Optional[str] = None

    assigned_to: Optional[int] = None

