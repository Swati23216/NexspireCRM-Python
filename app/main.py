from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.db.database import init_db
from app.models.followup import FollowUp
from app.models.lead import Lead

from app.routers.user_router import router as user_router
from app.routers.role_router import router as role_router
from app.routers.auth_router import router as auth_router
from app.routers.admin_router import router as admin_router
from app.routers.lead_router import router as lead_router
from app.routers.followup_router import router as followup_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.customer_router import router as customer_router
from app.routers.opportunity_router import router as opportunity_router
from app.routers.activity_router import router as activity_router
from app.routers.ticket_router import router as ticket_router
from app.routers.notification_router import router as notification_router
from app.routers.reports_router import router as reports_router
from app.routers.search_router import router as search_router

# ============================================================

# LOGGING

# ============================================================

logging.basicConfig(
level=logging.INFO,
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ============================================================

# FASTAPI APPLICATION

# ============================================================

app = FastAPI(
title="Nexspire CRM API",
version="1.0.0"
)

# ============================================================

# CORS

# ============================================================

app.add_middleware(
CORSMiddleware,


allow_origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500"
],

allow_credentials=True,

allow_methods=["*"],

allow_headers=["*"],


)

# ============================================================

# DATABASE STARTUP

# ============================================================

@app.on_event("startup")
async def startup_event():
    logging.info("Initializing database...")
    try:
        initialized = await init_db()
    except Exception:
        logging.exception("Startup database initialization failed")
        return

    if not initialized:
        return

    try:
        migrated_followups = 0
        followups = await FollowUp.find_all().to_list()
        for followup in followups:
            if followup.subject and followup.notes is not None:
                continue

            legacy_subject, separator, legacy_notes = (
                (followup.remarks or "").partition("\n")
            )
            if not followup.subject:
                followup.subject = (
                    legacy_subject.strip()
                    if separator
                    else ""
                )
                if not followup.subject and followup.lead_id is not None:
                    lead = await Lead.find_one(
                        Lead.lead_id == followup.lead_id
                    )
                    if lead:
                        followup.subject = f"Follow up with {lead.name}"
                if not followup.subject:
                    target = (
                        f"ticket #{followup.ticket_id}"
                        if followup.ticket_id is not None
                        else "customer"
                    )
                    followup.subject = f"Follow up on {target}"

            if followup.notes is None:
                followup.notes = (
                    legacy_notes.strip()
                    if separator
                    else (followup.remarks or "").strip()
                )

            await followup.save()
            migrated_followups += 1

        if migrated_followups:
            logging.info(
                "Migrated %s follow-ups to separate subject and notes fields",
                migrated_followups,
            )
    except Exception:
        logging.exception("Follow-up subject and notes migration failed")


# ============================================================

# ROOT

# ============================================================

@app.get("/health")
async def health():
  return {"status": "ok", "service": "Nexspire CRM"}


@app.get("/", include_in_schema=False)
async def company_homepage():
  return FileResponse(
    Path(__file__).resolve().parent.parent / "frontend" / "company.html"
  )


# ============================================================

# ROUTERS

# ============================================================

app.include_router(user_router)
app.include_router(role_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(lead_router)
app.include_router(followup_router)
app.include_router(dashboard_router)
app.include_router(customer_router)
app.include_router(opportunity_router)
app.include_router(activity_router)
app.include_router(ticket_router)
app.include_router(notification_router)
app.include_router(reports_router)
app.include_router(search_router)

# Serve the complete browser application from the same origin as the API.
app.mount(
  "/",
  StaticFiles(directory=Path(__file__).resolve().parent.parent / "frontend", html=True),
  name="frontend"
)
