from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.core.dependencies import require_role
from app.models.activity import Activity
from app.schemas.activity_schema import (
    ActivityCreate,
    ActivityUpdate
)


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)

ACTIVITY_ROLES = [
    "Admin",
    "Manager",
    "Sales Executive",
    "Calling Executive",
    "Marketing Executive",
    "HR",
    "Team Lead",
    "Operations Executive",
]


# ============================================================
# CREATE ACTIVITY
# ============================================================

@router.post("/")
async def create_activity(
    data: ActivityCreate,
    current_user=Depends(require_role(ACTIVITY_ROLES))
):

    # Find latest activity ID
    last_activity = await Activity.find_one(
        sort=[("activity_id", -1)]
    )

    if last_activity:
        activity_id = last_activity.activity_id + 1
    else:
        activity_id = 1

    activity = Activity(
        activity_id=activity_id,
        subject=data.subject,
        activity_type=data.activity_type,
        description=data.description,
        customer_id=data.customer_id,
        lead_id=data.lead_id,
        opportunity_id=data.opportunity_id,
        due_date=data.due_date,
        status=data.status,
        assigned_to=data.assigned_to,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    await activity.insert()

    return {
        "status": "success",
        "message": "Activity created successfully",
        "activity": activity
    }


# ============================================================
# GET ALL ACTIVITIES
# ============================================================

@router.get("/")
async def get_activities(
    current_user=Depends(require_role(ACTIVITY_ROLES))
):

    activities = await Activity.find(
        Activity.is_active == True
    ).sort(
        [("activity_id", -1)]
    ).to_list()

    return {
        "status": "success",
        "count": len(activities),
        "activities": activities
    }


# ============================================================
# GET ACTIVITY BY ID
# ============================================================

@router.get("/{activity_id}")
async def get_activity(
    activity_id: int,
    current_user=Depends(require_role(ACTIVITY_ROLES))
):

    activity = await Activity.find_one(
        Activity.activity_id == activity_id
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return {
        "status": "success",
        "activity": activity
    }


# ============================================================
# UPDATE ACTIVITY
# ============================================================

@router.put("/{activity_id}")
async def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    current_user=Depends(require_role(ACTIVITY_ROLES))
):

    activity = await Activity.find_one(
        Activity.activity_id == activity_id
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(activity, field, value)

    activity.updated_at = datetime.utcnow()

    await activity.save()

    return {
        "status": "success",
        "message": "Activity updated successfully",
        "activity": activity
    }


# ============================================================
# DELETE ACTIVITY
# ============================================================

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user=Depends(require_role(["Admin"]))
):

    activity = await Activity.find_one(
        Activity.activity_id == activity_id
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    activity.is_active = False
    activity.updated_at = datetime.utcnow()

    await activity.save()

    return {
        "status": "success",
        "message": "Activity deleted successfully"
    }