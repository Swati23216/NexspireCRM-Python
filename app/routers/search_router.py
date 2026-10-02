from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, require_permission
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.models.activity import Activity
from app.models.ticket import Ticket
from app.models.notification import Notification


router = APIRouter(
    prefix="/search",
    tags=["Search & Filtering"]
)


# ============================================================
# CUSTOMERS SEARCH
# ============================================================

@router.get("/customers")
async def search_customers(
    search: str | None = Query(None),
    email: str | None = Query(None),
    mobile: str | None = Query(None),
    current_user=Depends(require_permission("customers.view")),
):

    customers = await Customer.find_all().to_list()

    results = []

    for customer in customers:

        name = str(getattr(customer, "full_name", "") or
                   getattr(customer, "name", ""))

        customer_email = str(
            getattr(customer, "email", "") or ""
        )

        customer_mobile = str(
            getattr(customer, "mobile_no", "") or
            getattr(customer, "phone", "") or ""
        )

        if search:
            value = search.lower()

            if (
                value not in name.lower()
                and value not in customer_email.lower()
                and value not in customer_mobile.lower()
            ):
                continue

        if email and email.lower() not in customer_email.lower():
            continue

        if mobile and mobile not in customer_mobile:
            continue

        results.append(customer.model_dump(mode="json"))

    return {
        "status": "success",
        "module": "customers",
        "count": len(results),
        "results": results
    }


# ============================================================
# LEADS SEARCH
# ============================================================

@router.get("/leads")
async def search_leads(
    search: str | None = Query(None),
    status: str | None = Query(None),
    source: str | None = Query(None),
    assigned_to: int | None = Query(None),
    current_user=Depends(require_permission("leads.view")),
):

    leads = await Lead.find_all().to_list()

    results = []

    for lead in leads:

        name = str(
            getattr(lead, "name", "") or ""
        )

        email = str(
            getattr(lead, "email", "") or ""
        )

        phone = str(
            getattr(lead, "phone", "") or
            getattr(lead, "mobile_no", "") or ""
        )

        lead_status = str(
            getattr(lead, "status", "") or ""
        )

        lead_source = str(
            getattr(lead, "source", "") or ""
        )

        lead_assigned = getattr(
            lead,
            "assigned_to",
            None
        )

        if search:

            value = search.lower()

            if (
                value not in name.lower()
                and value not in email.lower()
                and value not in phone.lower()
            ):
                continue

        if status and lead_status.lower() != status.lower():
            continue

        if source and lead_source.lower() != source.lower():
            continue

        if assigned_to is not None and lead_assigned != assigned_to:
            continue

        results.append(lead.model_dump(mode="json"))

    return {
        "status": "success",
        "module": "leads",
        "count": len(results),
        "results": results
    }


# ============================================================
# OPPORTUNITIES SEARCH
# ============================================================

@router.get("/opportunities")
async def search_opportunities(
    search: str | None = Query(None),
    stage: str | None = Query(None),
    assigned_to: int | None = Query(None),
    current_user=Depends(get_current_user),
):

    opportunities = await Opportunity.find_all().to_list()

    results = []

    for opportunity in opportunities:

        subject = str(
            getattr(opportunity, "subject", "") or ""
        )

        description = str(
            getattr(opportunity, "description", "") or ""
        )

        opportunity_stage = str(
            getattr(opportunity, "stage", "") or ""
        )

        opportunity_assigned = getattr(
            opportunity,
            "assigned_to",
            None
        )

        if search:

            value = search.lower()

            if (
                value not in subject.lower()
                and value not in description.lower()
            ):
                continue

        if stage and opportunity_stage.lower() != stage.lower():
            continue

        if (
            assigned_to is not None
            and opportunity_assigned != assigned_to
        ):
            continue

        results.append(
            opportunity.model_dump(mode="json")
        )

    return {
        "status": "success",
        "module": "opportunities",
        "count": len(results),
        "results": results
    }


# ============================================================
# ACTIVITIES SEARCH
# ============================================================

@router.get("/activities")
async def search_activities(
    search: str | None = Query(None),
    status: str | None = Query(None),
    activity_type: str | None = Query(None),
    assigned_to: int | None = Query(None),
    current_user=Depends(get_current_user),
):

    activities = await Activity.find_all().to_list()

    results = []

    for activity in activities:

        subject = str(
            getattr(activity, "subject", "") or ""
        )

        description = str(
            getattr(activity, "description", "") or ""
        )

        activity_status = str(
            getattr(activity, "status", "") or ""
        )

        activity_type_value = str(
            getattr(activity, "activity_type", "") or ""
        )

        activity_assigned = getattr(
            activity,
            "assigned_to",
            None
        )

        if search:

            value = search.lower()

            if (
                value not in subject.lower()
                and value not in description.lower()
            ):
                continue

        if status and activity_status.lower() != status.lower():
            continue

        if (
            activity_type
            and activity_type_value.lower() != activity_type.lower()
        ):
            continue

        if (
            assigned_to is not None
            and activity_assigned != assigned_to
        ):
            continue

        results.append(
            activity.model_dump(mode="json")
        )

    return {
        "status": "success",
        "module": "activities",
        "count": len(results),
        "results": results
    }


# ============================================================
# TICKETS SEARCH
# ============================================================

@router.get("/tickets")
async def search_tickets(
    search: str | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    assigned_to: int | None = Query(None),
    current_user=Depends(get_current_user),
):

    tickets = await Ticket.find_all().to_list()

    results = []

    for ticket in tickets:

        subject = str(
            getattr(ticket, "subject", "") or ""
        )

        description = str(
            getattr(ticket, "description", "") or ""
        )

        ticket_status = str(
            getattr(ticket, "status", "") or ""
        )

        ticket_priority = str(
            getattr(ticket, "priority", "") or ""
        )

        ticket_assigned = getattr(
            ticket,
            "assigned_to",
            None
        )

        if search:

            value = search.lower()

            if (
                value not in subject.lower()
                and value not in description.lower()
            ):
                continue

        if status and ticket_status.lower() != status.lower():
            continue

        if (
            priority
            and ticket_priority.lower() != priority.lower()
        ):
            continue

        if (
            assigned_to is not None
            and ticket_assigned != assigned_to
        ):
            continue

        results.append(
            ticket.model_dump(mode="json")
        )

    return {
        "status": "success",
        "module": "tickets",
        "count": len(results),
        "results": results
    }


# ============================================================
# NOTIFICATIONS SEARCH
# ============================================================

@router.get("/notifications")
async def search_notifications(
    search: str | None = Query(None),
    notification_type: str | None = Query(None),
    is_read: bool | None = Query(None),
    user_id: int | None = Query(None),
    current_user=Depends(get_current_user),
):

    notifications = await Notification.find_all().to_list()

    results = []

    for notification in notifications:

        title = str(
            getattr(notification, "title", "") or ""
        )

        message = str(
            getattr(notification, "message", "") or ""
        )

        notification_type_value = str(
            getattr(notification, "notification_type", "") or ""
        )

        notification_is_read = getattr(
            notification,
            "is_read",
            None
        )

        notification_user = getattr(
            notification,
            "user_id",
            None
        )

        if search:

            value = search.lower()

            if (
                value not in title.lower()
                and value not in message.lower()
            ):
                continue

        if (
            notification_type
            and notification_type_value.lower()
            != notification_type.lower()
        ):
            continue

        if (
            is_read is not None
            and notification_is_read != is_read
        ):
            continue

        if current_user["role_name"] == "Admin":
            if user_id is not None and notification_user != user_id:
                continue
        elif notification_user != current_user["user_id"]:
            continue

        results.append(
            notification.model_dump(mode="json")
        )

    return {
        "status": "success",
        "module": "notifications",
        "count": len(results),
        "results": results
    }


# ============================================================
# GLOBAL SEARCH
# ============================================================

@router.get("/global")
async def global_search(
    search: str = Query(..., min_length=1),
    current_user=Depends(get_current_user),
):

    value = search.lower()

    results = {
        "customers": [],
        "leads": [],
        "opportunities": [],
        "activities": [],
        "tickets": [],
        "notifications": []
    }

    permissions = set(current_user.get("permissions", []))

    if "customers.view" in permissions or current_user.get("role_name") == "Admin":
        customers = await Customer.find_all().to_list()
        for item in customers:
            data = item.model_dump(mode="json")
            if value in str(data).lower():
                results["customers"].append(data)

    if "leads.view" in permissions or current_user.get("role_name") == "Admin":
        leads = await Lead.find_all().to_list()
        for item in leads:
            data = item.model_dump(mode="json")
            if value in str(data).lower():
                results["leads"].append(data)

    # ---------------- OPPORTUNITIES ----------------

    opportunities = await Opportunity.find_all().to_list()

    for item in opportunities:

        data = item.model_dump(mode="json")

        if value in str(data).lower():
            results["opportunities"].append(data)

    # ---------------- ACTIVITIES ----------------

    activities = await Activity.find_all().to_list()

    for item in activities:

        data = item.model_dump(mode="json")

        if value in str(data).lower():
            results["activities"].append(data)

    # ---------------- TICKETS ----------------

    tickets = await Ticket.find_all().to_list()

    for item in tickets:

        data = item.model_dump(mode="json")

        if value in str(data).lower():
            results["tickets"].append(data)

    # ---------------- NOTIFICATIONS ----------------

    notifications = await Notification.find_all().to_list()

    for item in notifications:

        if (
            current_user["role_name"] != "Admin"
            and item.user_id != current_user["user_id"]
        ):
            continue

        data = item.model_dump(mode="json")

        if value in str(data).lower():
            results["notifications"].append(data)

    total_results = sum(
        len(items)
        for items in results.values()
    )

    return {
        "status": "success",
        "search": search,
        "total_results": total_results,
        "results": results
    }