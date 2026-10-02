import logging

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings

from app.models.role import Role
from app.models.user import User
from app.models.lead import Lead
from app.models.followup import FollowUp
from app.models.customer import Customer
from app.models.opportunity import Opportunity
from app.models.activity import Activity
from app.models.ticket import Ticket
from app.models.notification import Notification


client = AsyncIOMotorClient(
    settings.MONGODB_URL,
    serverSelectionTimeoutMS=5000,
)

database = client[settings.DATABASE_NAME]

async def init_db():
    try:
        await init_beanie(
            database=database,
            document_models=[
                Role,
                User,
                Lead,
                FollowUp,
                Customer,
                Opportunity,
                Activity,
                Ticket,
                Notification,
            ],
        )
        logging.info("Database initialized successfully")
    except Exception:
        logging.exception("Database initialization failed. The API will continue running without MongoDB connectivity.")
        return False
    return True
    