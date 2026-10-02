from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

from app.core.dependencies import require_role
from app.models.notification import (
    Notification,
    NotificationCreate,
    NotificationUpdate
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

NOTIFICATION_ROLES = [
    "Admin",
    "Support Executive",
    "HR",
    "Operations Executive",
]


def _can_access_notification(notification, current_user):
    return (
        current_user["role_name"] == "Admin"
        or notification.user_id == current_user["user_id"]
    )


# ============================================================
# CREATE NOTIFICATION
# ============================================================

@router.post("/")
async def create_notification(
    data: NotificationCreate,
    current_user=Depends(require_role(NOTIFICATION_ROLES)),
):
    if (
        current_user["role_name"] != "Admin"
        and data.user_id != current_user["user_id"]
    ):
        raise HTTPException(status_code=403, detail="Cannot create a notification for another user")

    last_notification = await Notification.find_one(
        {},
        sort=[("notification_id", -1)]
    )

    if last_notification:
        notification_id = last_notification.notification_id + 1
    else:
        notification_id = 1

    notification = Notification(
        notification_id=notification_id,

        user_id=data.user_id,
        title=data.title,
        message=data.message,

        notification_type=data.notification_type,

        customer_id=data.customer_id,
        lead_id=data.lead_id,
        opportunity_id=data.opportunity_id,
        activity_id=data.activity_id,
        ticket_id=data.ticket_id,

        is_read=False,
        is_active=True,

        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    await notification.insert()

    return {
        "status": "success",
        "message": "Notification created successfully",
        "notification": notification
    }


# ============================================================
# GET ALL NOTIFICATIONS
# ============================================================

@router.get("/")
async def get_notifications(
    user_id: int | None = None,
    is_read: bool | None = None,
    current_user=Depends(require_role(NOTIFICATION_ROLES)),
):

    query = {
        "is_active": True
    }

    if current_user["role_name"] != "Admin":
        query["user_id"] = current_user["user_id"]
    elif user_id is not None:
        query["user_id"] = user_id

    if is_read is not None:
        query["is_read"] = is_read

    notifications = await Notification.find(
        query
    ).sort(
        [("created_at", -1)]
    ).to_list()

    return {
        "status": "success",
        "count": len(notifications),
        "notifications": notifications
    }
# ============================================================
# MARK AS READ
# ============================================================

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user=Depends(require_role(NOTIFICATION_ROLES)),
):

    notification = await Notification.find_one(
        Notification.notification_id == notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if not _can_access_notification(notification, current_user):
        raise HTTPException(status_code=403, detail="Cannot access another user's notification")

    notification.is_read = True
    notification.updated_at = datetime.now(timezone.utc)

    await notification.save()

    return {
        "status": "success",
        "message": "Notification marked as read",
        "notification": notification
    }


# ============================================================
# UPDATE NOTIFICATION
# ============================================================

@router.put("/{notification_id}")
async def update_notification(
    notification_id: int,
    data: NotificationUpdate,
    current_user=Depends(require_role(NOTIFICATION_ROLES)),
):

    notification = await Notification.find_one(
        Notification.notification_id == notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if not _can_access_notification(notification, current_user):
        raise HTTPException(status_code=403, detail="Cannot access another user's notification")

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(notification, field, value)

    notification.updated_at = datetime.now(timezone.utc)

    await notification.save()

    return {
        "status": "success",
        "message": "Notification updated successfully",
        "notification": notification
    }


# ============================================================
# DELETE NOTIFICATION
# ============================================================

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user=Depends(require_role(NOTIFICATION_ROLES)),
):

    notification = await Notification.find_one(
        Notification.notification_id == notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if not _can_access_notification(notification, current_user):
        raise HTTPException(status_code=403, detail="Cannot access another user's notification")

    await notification.delete()

    return {
        "status": "success",
        "message": "Notification deleted successfully"
    }