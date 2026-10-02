from fastapi import APIRouter, Depends

from app.models.user import User
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.opportunity import Opportunity
from app.models.activity import Activity
from app.models.followup import FollowUp
from app.models.ticket import Ticket

from app.core.dependencies import get_current_user, require_permission


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@router.get("/summary")
async def dashboard_summary(
    current_user=Depends(get_current_user)
):

    # --------------------------------------------------------
    # COUNTS
    # --------------------------------------------------------

    total_users = await User.find(
        User.is_active == True
    ).count()

    total_customers = await Customer.find_all().count()

    total_leads = await Lead.find_all().count()

    total_opportunities = await Opportunity.find(
        Opportunity.is_active == True
    ).count()

    total_activities = await Activity.find(
        Activity.is_active == True
    ).count()

    total_tickets = await Ticket.find(
        Ticket.is_active == True
    ).count()

    total_followups = await FollowUp.find_all().count()


    # --------------------------------------------------------
    # LEAD STATUS
    # --------------------------------------------------------

    new_leads = await Lead.find(
        Lead.status == "New"
    ).count()

    contacted_leads = await Lead.find(
        Lead.status == "Contacted"
    ).count()

    qualified_leads = await Lead.find(
        Lead.status == "Qualified"
    ).count()

    converted_leads = await Lead.find(
        Lead.status == "Converted"
    ).count()


    # --------------------------------------------------------
    # OPPORTUNITIES
    # --------------------------------------------------------

    opportunities = await Opportunity.find(
        Opportunity.is_active == True
    ).to_list()

    open_opportunities = 0
    won_opportunities = 0
    lost_opportunities = 0

    total_opportunity_value = 0
    won_revenue = 0


    for opportunity in opportunities:

        amount = opportunity.amount or 0

        total_opportunity_value += amount

        if opportunity.stage == "Closed Won":

            won_opportunities += 1
            won_revenue += amount

        elif opportunity.stage == "Closed Lost":

            lost_opportunities += 1

        else:

            open_opportunities += 1


    # --------------------------------------------------------
    # ACTIVITY STATUS
    # --------------------------------------------------------

    pending_activities = await Activity.find(
        Activity.is_active == True,
        Activity.status == "Pending"
    ).count()

    completed_activities = await Activity.find(
        Activity.is_active == True,
        Activity.status == "Completed"
    ).count()


    # --------------------------------------------------------
    # TICKET STATUS
    # --------------------------------------------------------

    open_tickets = await Ticket.find(
        Ticket.is_active == True,
        Ticket.status == "Open"
    ).count()

    pending_tickets = await Ticket.find(
        Ticket.is_active == True,
        Ticket.status == "Pending"
    ).count()

    resolved_tickets = await Ticket.find(
        Ticket.is_active == True,
        Ticket.status == "Resolved"
    ).count()


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "status": "success",

        "summary": {

            "total_users": total_users if current_user.get("role_name") == "Admin" else 0,

            "total_customers": total_customers if "customers.view" in current_user.get("permissions", []) else 0,

            "total_leads": total_leads if "leads.view" in current_user.get("permissions", []) else 0,

            "total_opportunities": total_opportunities,

            "total_activities": total_activities,

            "total_followups": total_followups if "followups.view" in current_user.get("permissions", []) else 0,

            "total_tickets": total_tickets,

            "won_revenue": won_revenue
        },

        "leads": {

            "new": new_leads if "leads.view" in current_user.get("permissions", []) else 0,

            "contacted": contacted_leads if "leads.view" in current_user.get("permissions", []) else 0,

            "qualified": qualified_leads if "leads.view" in current_user.get("permissions", []) else 0,

            "converted": converted_leads if "leads.view" in current_user.get("permissions", []) else 0
        },

        "opportunities": {

            "open": open_opportunities,

            "won": won_opportunities,

            "lost": lost_opportunities,

            "total_value": total_opportunity_value,

            "won_revenue": won_revenue
        },

        "activities": {

            "pending": pending_activities,

            "completed": completed_activities
        },

        "tickets": {

            "open": open_tickets,

            "pending": pending_tickets,

            "resolved": resolved_tickets
        }

    }


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

@router.get("/overview")
async def dashboard_overview(
    current_user=Depends(get_current_user)
):

    total_users = await User.find_all().count()

    active_users = await User.find(
        User.is_active == True
    ).count()

    total_leads = await Lead.find_all().count()

    total_followups = await FollowUp.find_all().count()

    total_customers = await Customer.find_all().count()

    total_opportunities = await Opportunity.find(
        Opportunity.is_active == True
    ).count()

    total_activities = await Activity.find(
        Activity.is_active == True
    ).count()

    total_tickets = await Ticket.find(
        Ticket.is_active == True
    ).count()

    permissions = set(current_user.get("permissions", []))

    return {

        "status": "success",

        "overview": {

            "total_users": total_users if current_user.get("role_name") == "Admin" else 0,

            "active_users": active_users if current_user.get("role_name") == "Admin" else 0,

            "total_leads": total_leads if "leads.view" in permissions else 0,

            "total_customers": total_customers if "customers.view" in permissions else 0,

            "total_opportunities": total_opportunities,

            "total_activities": total_activities,

            "total_followups": total_followups if "followups.view" in permissions else 0,

            "total_tickets": total_tickets
        }

    }


# ============================================================
# LEADS BY STATUS
# ============================================================

@router.get("/leads/status")
async def leads_by_status(
    current_user=Depends(require_permission("leads.view"))
):

    statuses = [
        "New",
        "Contacted",
        "Interested",
        "Follow-up",
        "Demo Scheduled",
        "Proposal Sent",
        "Negotiation",
        "Converted",
        "Hold",
        "Lost"
    ]

    result = {}

    for status in statuses:

        result[status] = await Lead.find(
            Lead.status == status
        ).count()


    return {

        "status": "success",

        "lead_status": result

    }


# ============================================================
# RECENT LEADS
# ============================================================

@router.get("/recent-leads")
async def recent_leads(
    current_user=Depends(require_permission("leads.view"))
):

    leads = await Lead.find_all().sort(
        -Lead.created_at
    ).limit(10).to_list()

    return {

        "status": "success",

        "leads": leads

    }


# ============================================================
# UPCOMING FOLLOW-UPS
# ============================================================

@router.get("/upcoming-followups")
async def upcoming_followups(
    current_user=Depends(require_permission("followups.view"))
):

    followups = await FollowUp.find_all().sort(
        FollowUp.next_followup_date
    ).limit(10).to_list()

    return {

        "status": "success",

        "followups": followups

    }


# ============================================================
# LEAD REPORT
# ============================================================

@router.get("/leads")
async def lead_report(
    current_user=Depends(require_permission("leads.view"))
):

    total = await Lead.find_all().count()

    new = await Lead.find(
        Lead.status == "New"
    ).count()

    contacted = await Lead.find(
        Lead.status == "Contacted"
    ).count()

    qualified = await Lead.find(
        Lead.status == "Qualified"
    ).count()

    converted = await Lead.find(
        Lead.status == "Converted"
    ).count()


    return {

        "status": "success",

        "report": {

            "total": total,

            "new": new,

            "contacted": contacted,

            "qualified": qualified,

            "converted": converted

        }

    }


# ============================================================
# OPPORTUNITY REPORT
# ============================================================

@router.get("/opportunities")
async def opportunity_report(
    current_user=Depends(get_current_user)
):

    opportunities = await Opportunity.find_all().to_list()

    total = len(opportunities)

    open_count = 0

    won_count = 0

    lost_count = 0

    total_value = 0

    won_revenue = 0


    for opportunity in opportunities:

        amount = opportunity.amount or 0

        total_value += amount


        if opportunity.stage == "Closed Won":

            won_count += 1

            won_revenue += amount


        elif opportunity.stage == "Closed Lost":

            lost_count += 1


        else:

            open_count += 1


    return {

        "status": "success",

        "report": {

            "total": total,

            "open": open_count,

            "won": won_count,

            "lost": lost_count,

            "total_value": total_value,

            "won_revenue": won_revenue

        }

    }


# ============================================================
# ACTIVITY REPORT
# ============================================================

@router.get("/activities")
async def activity_report(
    current_user=Depends(get_current_user)
):

    total = await Activity.find_all().count()

    pending = await Activity.find(
        Activity.status == "Pending"
    ).count()

    completed = await Activity.find(
        Activity.status == "Completed"
    ).count()

    cancelled = await Activity.find(
        Activity.status == "Cancelled"
    ).count()


    return {

        "status": "success",

        "report": {

            "total": total,

            "pending": pending,

            "completed": completed,

            "cancelled": cancelled

        }

    }


# ============================================================
# TICKET REPORT
# ============================================================

@router.get("/tickets")
async def ticket_report(
    current_user=Depends(get_current_user)
):

    total = await Ticket.find_all().count()

    open_count = await Ticket.find(
        Ticket.status == "Open"
    ).count()

    pending = await Ticket.find(
        Ticket.status == "Pending"
    ).count()

    resolved = await Ticket.find(
        Ticket.status == "Resolved"
    ).count()

    closed = await Ticket.find(
        Ticket.status == "Closed"
    ).count()


    return {

        "status": "success",

        "report": {

            "total": total,

            "open": open_count,

            "pending": pending,

            "resolved": resolved,

            "closed": closed

        }

    }


# ============================================================
# REVENUE REPORT
# ============================================================

@router.get("/revenue")
async def revenue_report(
    current_user=Depends(get_current_user)
):

    opportunities = await Opportunity.find_all().to_list()

    total_pipeline = 0

    won_revenue = 0

    lost_value = 0


    for opportunity in opportunities:

        amount = opportunity.amount or 0

        total_pipeline += amount


        if opportunity.stage == "Closed Won":

            won_revenue += amount


        elif opportunity.stage == "Closed Lost":

            lost_value += amount


    return {

        "status": "success",

        "revenue": {

            "total_pipeline": total_pipeline,

            "won_revenue": won_revenue,

            "lost_value": lost_value

        }

    }