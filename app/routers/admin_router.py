from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.models.user import User
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.followup import FollowUp


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
async def admin_dashboard(
    current_user=Depends(
        require_role(["Admin"])
    )
):

    # Count total users
    total_users = await User.count()

    # Count total leads
    total_leads = await Lead.count()

    # Count total customers
    total_customers = await Customer.count()

    # Count total follow-ups
    total_followups = await FollowUp.count()

    return {
        "message": "Welcome Admin",

        "user": current_user,

        "dashboard": {
            "total_users": total_users,
            "total_leads": total_leads,
            "total_customers": total_customers,
            "total_followups": total_followups
        }
    }