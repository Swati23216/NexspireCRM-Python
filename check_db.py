import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    try:
        await client.admin.command("ping")
        print("MongoDB ping succeeded")
        print("Database:", db.name)

        collections = await db.list_collection_names()
        print("Collections:", collections)

        roles = await db["roles"].find().to_list(None)
        print("Roles:", roles)
    finally:
        client.close()

asyncio.run(main())