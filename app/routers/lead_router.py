from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.lead import Lead
from app.models.customer import Customer
from app.core.dependencies import get_current_user, require_permission, require_role
from app.schemas.lead_schema import (
    LeadCreate,
    LeadUpdate,
    AssignLead,
    PublicInquiry
)


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)


@router.post("/public-inquiries", status_code=status.HTTP_201_CREATED)
async def create_public_inquiry(data: PublicInquiry):
    if data.website:
        return {"message": "Thanks, your request has been received."}

    latest_lead = await Lead.find_all().sort(
        -Lead.lead_id
    ).first_or_none()

    lead = Lead(
        lead_id=latest_lead.lead_id + 1 if latest_lead else 1,
        name=data.name.strip(),
        email=str(data.email).lower(),
        phone=data.phone.strip(),
        company=data.company.strip(),
        source="Website",
        status="New",
        service_interest=data.service_interest.strip(),
        message=data.message.strip()
    )
    await lead.insert()

    return {
        "message": "Thanks, your request has been received.",
        "lead_id": lead.lead_id
    }


# =========================================================
# CREATE LEAD
# Admin, Manager, Sales, Calling, Marketing
# =========================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    current_user=Depends(require_permission("leads.create"))
):

    # Generate next numeric CRM lead_id
    latest_lead = await Lead.find_all().sort(
        -Lead.lead_id
    ).first_or_none()

    if latest_lead:
        next_lead_id = latest_lead.lead_id + 1
    else:
        next_lead_id = 1

    lead = Lead(
        lead_id=next_lead_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        source=data.source,
        status="New"
    )

    await lead.insert()

    return {
        "message": "Lead created successfully",
        "lead_id": lead.lead_id
    }


# =========================================================
# GET DASHBOARD STATS
# Authenticated users
# =========================================================

@router.get("/dashboard/stats")
async def dashboard_stats(
    current_user=Depends(require_permission("leads.view"))
):

    total = await Lead.find_all().count()

    new = await Lead.find(
        Lead.status == "New"
    ).count()

    contacted = await Lead.find(
        Lead.status == "Contacted"
    ).count()

    return {
        "total_leads": total,
        "new_leads": new,
        "contacted_leads": contacted
    }


# =========================================================
# SEARCH LEADS
# Authenticated users
# =========================================================

@router.get("/search/{name}")
async def search_leads(
    name: str,
    current_user=Depends(require_permission("leads.view"))
):

    return await Lead.find(
        {
            "name": {
                "$regex": name,
                "$options": "i"
            }
        }
    ).to_list()


# =========================================================
# GET ALL LEADS
# Authenticated users
# =========================================================

@router.get("/")
async def get_leads(
    current_user=Depends(require_permission("leads.view"))
):

    return await Lead.find_all().to_list()


# =========================================================
# GET SINGLE LEAD
# Authenticated users
# =========================================================

@router.get("/{lead_id}")
async def get_lead(
    lead_id: int,
    current_user=Depends(require_permission("leads.view"))
):

    lead = await Lead.find_one(
        Lead.lead_id == lead_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


# =========================================================
# UPDATE LEAD
# Admin, Manager, Sales, Calling, Marketing
# =========================================================

@router.put("/{lead_id}")
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    current_user=Depends(require_permission("leads.update"))
):

    lead = await Lead.find_one(
        Lead.lead_id == lead_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    if data.name is not None:
        lead.name = data.name

    if data.email is not None:
        lead.email = data.email

    if data.phone is not None:
        lead.phone = data.phone

    if data.company is not None:
        lead.company = data.company

    if data.source is not None:
        lead.source = data.source

    if data.status is not None:
        lead.status = data.status

    if data.assigned_to is not None:
        lead.assigned_to = data.assigned_to

    await lead.save()

    return {
        "message": "Lead updated successfully",
        "lead": lead
    }


# =========================================================
# ASSIGN LEAD
# ADMIN ONLY
# =========================================================

@router.put("/{lead_id}/assign")
async def assign_lead(
    lead_id: int,
    data: AssignLead,
    current_user=Depends(
        require_role(["Admin"])
    )
):

    lead = await Lead.find_one(
        Lead.lead_id == lead_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    lead.assigned_to = data.user_id

    await lead.save()

    return {
        "message": "Lead assigned successfully",
        "lead_id": lead.lead_id,
        "assigned_to": data.user_id
    }


# =========================================================
# CONVERT LEAD TO CUSTOMER
# Admin, Manager, Sales Executive
# =========================================================

@router.post("/{lead_id}/convert")
async def convert_lead(
    lead_id: int,
    current_user=Depends(require_permission("leads.convert"))
):

    lead = await Lead.find_one(
        Lead.lead_id == lead_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    if lead.status == "Converted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lead is already converted"
        )

    latest_customer = await Customer.find_all().sort(
        -Customer.customer_id
    ).first_or_none()
    next_customer_id = (
        latest_customer.customer_id + 1
        if latest_customer else 1
    )

    customer = Customer(
        customer_id=next_customer_id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        source=lead.source,
        created_by=current_user.get("user_id")
    )
    await customer.insert()

    lead.status = "Converted"
    lead.updated_at = datetime.utcnow()
    await lead.save()

    return {
        "message": "Lead converted successfully",
        "lead_id": lead.lead_id,
        "customer_id": customer.customer_id
    }


# =========================================================
# DELETE LEAD
# ADMIN ONLY
# =========================================================

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    current_user=Depends(require_permission("leads.delete"))
):

    lead = await Lead.find_one(
        Lead.lead_id == lead_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    await lead.delete()

    return {
        "message": "Lead deleted successfully",
        "lead_id": lead.lead_id
    }
