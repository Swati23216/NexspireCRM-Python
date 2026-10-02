from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.core.dependencies import require_role
from app.models.ticket import Ticket
from app.schemas.ticket_schema import TicketCreate, TicketUpdate


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

TICKET_ROLES = [
    "Admin",
    "Manager",
    "Support Executive",
    "Operations Executive",
]


# =========================================================
# CREATE TICKET
# =========================================================

@router.post("")
@router.post("/")
async def create_ticket(
    data: TicketCreate,
    current_user=Depends(require_role(TICKET_ROLES))
):

    last_ticket = await Ticket.find_one(
        sort=[("ticket_id", -1)]
    )

    ticket_id = (
        last_ticket.ticket_id + 1
        if last_ticket
        else 1
    )

    ticket = Ticket(
        ticket_id=ticket_id,

        # IMPORTANT:
        # Schema uses title
        # Database model uses subject
        subject=data.title,

        description=data.description,

        customer_id=data.customer_id,

        priority=data.priority,

        status=data.status,

        category=data.category,

        assigned_to=data.assigned_to,

        is_active=True,

        created_at=datetime.utcnow(),

        updated_at=datetime.utcnow()
    )

    await ticket.insert()

    return {
        "status": "success",
        "message": "Ticket created successfully",
        "ticket": ticket
    }


# =========================================================
# GET ALL TICKETS
# =========================================================

@router.get("")
@router.get("/")
async def get_tickets(
    current_user=Depends(require_role(TICKET_ROLES))
):

    tickets = await Ticket.find(
        Ticket.is_active == True
    ).sort(
        [("ticket_id", -1)]
    ).to_list()

    return {
        "status": "success",
        "count": len(tickets),
        "tickets": tickets
    }


# =========================================================
# GET SINGLE TICKET
# =========================================================

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    current_user=Depends(require_role(TICKET_ROLES))
):

    ticket = await Ticket.find_one(
        Ticket.ticket_id == ticket_id,
        Ticket.is_active == True
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "status": "success",
        "ticket": ticket
    }


# =========================================================
# UPDATE TICKET
# =========================================================

@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    current_user=Depends(require_role(TICKET_ROLES))
):

    ticket = await Ticket.find_one(
        Ticket.ticket_id == ticket_id,
        Ticket.is_active == True
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    # Frontend/schema uses "title"
    # Database model uses "subject"
    if "title" in update_data:

        ticket.subject = update_data.pop("title")

    if "priority" in update_data:

        ticket.priority = update_data["priority"]

    if "description" in update_data:

        ticket.description = update_data["description"]

    if "status" in update_data:

        ticket.status = update_data["status"]

    if "customer_id" in update_data:

        ticket.customer_id = update_data["customer_id"]

    if "category" in update_data:

        ticket.category = update_data["category"]

    if "assigned_to" in update_data:

        ticket.assigned_to = update_data["assigned_to"]

    ticket.updated_at = datetime.utcnow()

    await ticket.save()

    return {
        "status": "success",
        "message": "Ticket updated successfully",
        "ticket": ticket
    }


# =========================================================
# DELETE TICKET
# =========================================================

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    current_user=Depends(require_role(["Admin"]))
):

    ticket = await Ticket.find_one(
        Ticket.ticket_id == ticket_id
    )

    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    ticket.is_active = False

    ticket.updated_at = datetime.utcnow()

    await ticket.save()

    return {
        "status": "success",
        "message": "Ticket deleted successfully",
        "ticket_id": ticket_id
    }