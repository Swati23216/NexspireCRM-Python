from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import require_role
from app.models.opportunity import Opportunity
from app.schemas.opportunity_schema import (
    OpportunityCreate,
    OpportunityUpdate,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"]
)

OPPORTUNITY_ROLES = [
    "Admin",
    "Manager",
    "Sales Executive",
    "Finance Executive",
    "Team Lead",
    "Business Development Executive",
]
OPPORTUNITY_EDIT_ROLES = [
    "Admin",
    "Manager",
    "Sales Executive",
    "Business Development Executive",
]


# ============================================================
# CREATE OPPORTUNITY
# ============================================================

@router.post("/")
async def create_opportunity(
    data: OpportunityCreate,
    current_user=Depends(require_role(OPPORTUNITY_EDIT_ROLES)),
):

    last_opportunity = await Opportunity.find_all().sort(
        -Opportunity.opportunity_id
    ).first_or_none()

    if last_opportunity:
        opportunity_id = last_opportunity.opportunity_id + 1
    else:
        opportunity_id = 1

    opportunity = Opportunity(
        opportunity_id=opportunity_id,
        name=data.name,
        customer_id=data.customer_id,
        lead_id=data.lead_id,
        description=data.description,
        amount=data.amount,
        stage=data.stage,
        probability=data.probability,
        expected_close_date=data.expected_close_date,
        assigned_to=data.assigned_to,
        is_active=data.is_active
    )

    await opportunity.insert()

    return {
        "status": "success",
        "message": "Opportunity created successfully",
        "opportunity": opportunity
    }


# ============================================================
# GET ALL OPPORTUNITIES
# ============================================================

@router.get("/")
async def get_opportunities(
    current_user=Depends(require_role(OPPORTUNITY_ROLES)),
):

    opportunities = await Opportunity.find(
        Opportunity.is_active == True
    ).to_list()

    return {
        "status": "success",
        "count": len(opportunities),
        "opportunities": opportunities
    }


# ============================================================
# GET OPPORTUNITY BY ID
# ============================================================

@router.get("/{opportunity_id}")
async def get_opportunity(
    opportunity_id: int,
    current_user=Depends(require_role(OPPORTUNITY_ROLES)),
):

    opportunity = await Opportunity.find_one(
        Opportunity.opportunity_id == opportunity_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    return {
        "status": "success",
        "opportunity": opportunity
    }


# ============================================================
# UPDATE OPPORTUNITY
# ============================================================

@router.put("/{opportunity_id}")
async def update_opportunity(
    opportunity_id: int,
    data: OpportunityUpdate,
    current_user=Depends(require_role(OPPORTUNITY_EDIT_ROLES))
):

    opportunity = await Opportunity.find_one(
        Opportunity.opportunity_id == opportunity_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(opportunity, field, value)

    opportunity.updated_at = datetime.utcnow()

    await opportunity.save()

    return {
        "status": "success",
        "message": "Opportunity updated successfully",
        "opportunity": opportunity
    }


# ============================================================
# DELETE OPPORTUNITY
# ============================================================

@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: int,
    current_user=Depends(require_role(["Admin"]))
):

    opportunity = await Opportunity.find_one(
        Opportunity.opportunity_id == opportunity_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    opportunity.is_active = False
    opportunity.updated_at = datetime.utcnow()

    await opportunity.save()

    return {
        "status": "success",
        "message": "Opportunity deleted successfully"
    }