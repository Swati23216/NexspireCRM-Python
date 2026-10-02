from beanie import Document
from pydantic import Field
from datetime import datetime

class Role(Document):
    role_id: int
    role_name: str
    permissions: list[str] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    class Settings:
        name = "roles"