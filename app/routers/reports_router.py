from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.models.activity import Activity
from app.models.ticket import Ticket


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

REPORT_ROLES = [
    "Admin",
    "Manager",
    "Marketing Executive",
    "HR",
    "Finance Executive",
    "Team Lead",
    "Operations Executive",
    "Viewer",
]


# ============================================================
# LEADS REPORT
# ============================================================

@router.get("/leads")
async def leads_report(current_user=Depends(require_role(REPORT_ROLES))):

    total = await Lead.count()

    new = await Lead.find(
        {"status": "New"}
    ).count()

    contacted = await Lead.find(
        {"status": "Contacted"}
    ).count()

    qualified = await Lead.find(
        {"status": "Qualified"}
    ).count()

    converted = await Lead.find(
        {"status": "Converted"}
    ).count()

    lost = await Lead.find(
        {"status": "Lost"}
    ).count()

    return {
        "status": "success",
        "report": {
            "total_leads": total,
            "new_leads": new,
            "contacted_leads": contacted,
            "qualified_leads": qualified,
            "converted_leads": converted,
            "lost_leads": lost
        }
    }


# ============================================================
# OPPORTUNITY REPORT
# ============================================================

@router.get("/opportunities")
async def opportunities_report(current_user=Depends(require_role(REPORT_ROLES))):

    opportunities = await Opportunity.find_all().to_list()

    total_opportunities = len(opportunities)

    total_pipeline = 0
    won_revenue = 0
    lost_value = 0

    won_opportunities = 0
    lost_opportunities = 0

    for opportunity in opportunities:

        amount = float(getattr(opportunity, "amount", 0) or 0)

        stage = str(
            getattr(opportunity, "stage", "")
        ).lower()

        total_pipeline += amount

        if stage in ["closed won", "won"]:
            won_revenue += amount
            won_opportunities += 1

        elif stage in ["closed lost", "lost"]:
            lost_value += amount
            lost_opportunities += 1

    return {
        "status": "success",
        "report": {
            "total_opportunities": total_opportunities,
            "total_pipeline": total_pipeline,
            "won_opportunities": won_opportunities,
            "won_revenue": won_revenue,
            "lost_opportunities": lost_opportunities,
            "lost_value": lost_value
        }
    }


# ============================================================
# ACTIVITY REPORT
# ============================================================

@router.get("/activities")
async def activities_report(current_user=Depends(require_role(REPORT_ROLES))):

    activities = await Activity.find_all().to_list()

    total = len(activities)

    pending = 0
    completed = 0
    overdue = 0

    from datetime import datetime

    now = datetime.utcnow()

    for activity in activities:

        status = str(
            getattr(activity, "status", "")
        ).lower()

        if status == "pending":
            pending += 1

            due_date = getattr(
                activity,
                "due_date",
                None
            )

            if due_date and due_date < now:
                overdue += 1

        elif status == "completed":
            completed += 1

    return {
        "status": "success",
        "report": {
            "total_activities": total,
            "pending_activities": pending,
            "completed_activities": completed,
            "overdue_activities": overdue
        }
    }


# ============================================================
# TICKET REPORT
# ============================================================

@router.get("/tickets")
async def tickets_report(current_user=Depends(require_role(REPORT_ROLES))):

    tickets = await Ticket.find_all().to_list()

    total = len(tickets)

    open_tickets = 0
    pending_tickets = 0
    resolved_tickets = 0
    closed_tickets = 0

    for ticket in tickets:

        status = str(
            getattr(ticket, "status", "")
        ).lower()

        if status == "open":
            open_tickets += 1

        elif status == "pending":
            pending_tickets += 1

        elif status == "resolved":
            resolved_tickets += 1

        elif status == "closed":
            closed_tickets += 1

    return {
        "status": "success",
        "report": {
            "total_tickets": total,
            "open_tickets": open_tickets,
            "pending_tickets": pending_tickets,
            "resolved_tickets": resolved_tickets,
            "closed_tickets": closed_tickets
        }
    }


# ============================================================
# SALES REPORT
# ============================================================

@router.get("/sales")
async def sales_report(current_user=Depends(require_role(REPORT_ROLES))):

    opportunities = await Opportunity.find_all().to_list()

    total_pipeline = 0
    won_revenue = 0
    lost_value = 0

    won_count = 0
    total_count = len(opportunities)

    for opportunity in opportunities:

        amount = float(
            getattr(opportunity, "amount", 0) or 0
        )

        stage = str(
            getattr(opportunity, "stage", "")
        ).lower()

        total_pipeline += amount

        if stage in ["closed won", "won"]:
            won_revenue += amount
            won_count += 1

        elif stage in ["closed lost", "lost"]:
            lost_value += amount

    win_rate = 0

    if total_count > 0:
        win_rate = round(
            (won_count / total_count) * 100,
            2
        )

    return {
        "status": "success",
        "report": {
            "total_pipeline": total_pipeline,
            "won_revenue": won_revenue,
            "lost_value": lost_value,
            "win_rate": win_rate
        }
    }


# ============================================================
# OVERALL PERFORMANCE REPORT
# ============================================================

@router.get("/performance")
async def performance_report(current_user=Depends(require_role(REPORT_ROLES))):

    total_leads = await Lead.count()

    total_opportunities = await Opportunity.count()

    total_activities = await Activity.count()

    total_tickets = await Ticket.count()

    opportunities = await Opportunity.find_all().to_list()

    won_revenue = 0

    for opportunity in opportunities:

        amount = float(
            getattr(opportunity, "amount", 0) or 0
        )

        stage = str(
            getattr(opportunity, "stage", "")
        ).lower()

        if stage in ["closed won", "won"]:
            won_revenue += amount

    return {
        "status": "success",
        "report": {
            "total_leads": total_leads,
            "total_opportunities": total_opportunities,
            "total_activities": total_activities,
            "total_tickets": total_tickets,
            "won_revenue": won_revenue
        }
    }