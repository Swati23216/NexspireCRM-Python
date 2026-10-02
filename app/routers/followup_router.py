from fastapi import APIRouter, Depends, HTTPException, status

from app.models.followup import FollowUp
from app.models.lead import Lead

from app.core.dependencies import require_permission

from app.schemas.followup_schema import (
    FollowUpCreate,
    FollowUpUpdate
)
from app.models.ticket import Ticket


router = APIRouter(
    prefix="/followups",
    tags=["Follow-Ups"]
)


def split_legacy_remarks(remarks: str | None) -> tuple[str, str]:
    if not remarks:
        return "", ""

    subject, separator, notes = remarks.partition("\n")
    if separator:
        return subject.strip(), notes.strip()
    return "", remarks.strip()


# =========================================================
# CREATE FOLLOW-UP
# Allowed: Admin, Manager, Sales Executive, Calling Executive
# =========================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_followup(
    data: FollowUpCreate,
    current_user=Depends(require_permission("followups.create"))
):

    # -----------------------------------------------------
    # A follow-up must belong to either a Lead or a Ticket
    # -----------------------------------------------------

    if data.lead_id is None and data.ticket_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either lead_id or ticket_id is required"
        )

    if data.lead_id is not None and data.ticket_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use either lead_id or ticket_id, not both"
        )

    # -----------------------------------------------------
    # Check Lead
    # -----------------------------------------------------

    if data.lead_id is not None:

        lead = await Lead.find_one(
            Lead.lead_id == data.lead_id
        )

        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )

    # -----------------------------------------------------
    # Check Ticket
    # -----------------------------------------------------

    if data.ticket_id is not None:

        ticket = await Ticket.find_one(
            Ticket.ticket_id == data.ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

    legacy_subject, legacy_notes = split_legacy_remarks(data.remarks)
    subject = (data.subject or "").strip() or legacy_subject
    if not subject:
        if data.lead_id is not None:
            subject = f"Follow up with {lead.name}"
        else:
            subject = f"Follow up on ticket #{data.ticket_id}"

    notes = (
        data.notes.strip()
        if data.notes is not None
        else legacy_notes or (data.remarks or "").strip()
    )
    remarks = data.remarks
    if remarks is None:
        remarks = "\n".join(part for part in (subject, notes) if part)

    # -----------------------------------------------------
    # Generate next INTEGER followup_id
    # -----------------------------------------------------

    last_followup = await FollowUp.find(
        sort=[("followup_id", -1)]
    ).first_or_none()

    if last_followup and last_followup.followup_id is not None:
        next_followup_id = last_followup.followup_id + 1
    else:
        next_followup_id = 1

    # -----------------------------------------------------
    # Create Follow-Up
    # -----------------------------------------------------

    followup = FollowUp(
        followup_id=next_followup_id,

        lead_id=data.lead_id,

        ticket_id=data.ticket_id,

        subject=subject,

        notes=notes,

        remarks=remarks,

        next_followup_date=data.next_followup_date,

        created_by=current_user["user_id"]
    )

    await followup.insert()

    return {
        "message": "Follow-up created successfully",

        "followup_id": followup.followup_id,

        "lead_id": followup.lead_id,

        "ticket_id": followup.ticket_id
    }


# =========================================================
# GET ALL FOLLOW-UPS
# Allowed: Admin, Manager, Sales Executive, Calling Executive
# =========================================================

@router.get("/")
async def get_followups(
    current_user=Depends(require_permission("followups.view"))
):

    return await FollowUp.find_all().to_list()


# =========================================================
# GET FOLLOW-UPS BY LEAD
# IMPORTANT: Keep this BEFORE /{followup_id}
# =========================================================

@router.get("/lead/{lead_id}")
async def get_followups_by_lead(
    lead_id: int,
    current_user=Depends(require_permission("followups.view"))
):

    # Search using INTEGER lead_id
    followups = await FollowUp.find(
        FollowUp.lead_id == lead_id
    ).to_list()

    return followups


# =========================================================
# GET FOLLOW-UP BY INTEGER FOLLOWUP ID
# Allowed: Admin, Manager, Sales Executive, Calling Executive
# =========================================================

@router.get("/{followup_id}")
async def get_followup(
    followup_id: int,
    current_user=Depends(require_permission("followups.view"))
):

    # IMPORTANT:
    # Do NOT use FollowUp.get(followup_id)
    # because .get() searches MongoDB ObjectId.
    #
    # We want our INTEGER followup_id.

    followup = await FollowUp.find_one(
        FollowUp.followup_id == followup_id
    )

    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    return followup


# =========================================================
# UPDATE FOLLOW-UP
# Allowed: Admin, Manager, Sales Executive, Calling Executive
# =========================================================

@router.put("/{followup_id}")
async def update_followup(
    followup_id: int,
    data: FollowUpUpdate,
    current_user=Depends(require_permission("followups.update"))
):

    # Find using INTEGER followup_id
    followup = await FollowUp.find_one(
        FollowUp.followup_id == followup_id
    )

    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    if data.remarks is not None:
        legacy_subject, legacy_notes = split_legacy_remarks(data.remarks)
        if data.subject is None and legacy_subject:
            followup.subject = legacy_subject
        if data.notes is None:
            followup.notes = legacy_notes or data.remarks.strip()

    if data.subject is not None:
        followup.subject = data.subject.strip()

    if data.notes is not None:
        followup.notes = data.notes.strip()

    if any(
        value is not None
        for value in (data.subject, data.notes, data.remarks)
    ):
        followup.remarks = "\n".join(
            part
            for part in (
                (followup.subject or "").strip(),
                (followup.notes or "").strip(),
            )
            if part
        )

    # -----------------------------------------------------
    # Update next follow-up date
    # -----------------------------------------------------

    if data.next_followup_date is not None:
        followup.next_followup_date = data.next_followup_date

    await followup.save()

    return {
        "message": "Follow-up updated successfully",
        "followup": followup
    }


# =========================================================
# DELETE FOLLOW-UP
# ADMIN ONLY
# =========================================================

@router.delete("/{followup_id}")
async def delete_followup(
    followup_id: int,
    current_user=Depends(require_permission("followups.delete"))
):

    # Find using INTEGER followup_id
    followup = await FollowUp.find_one(
        FollowUp.followup_id == followup_id
    )

    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )

    await followup.delete()

    return {
        "message": "Follow-up deleted successfully",
        "followup_id": followup_id
    }