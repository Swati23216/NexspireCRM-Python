from beanie import Document
from pydantic import Field
from pydantic import EmailStr
from datetime import datetime
from typing import Optional


class User(Document):
    user_id: int
    full_name: str
    email: EmailStr
    mobile_no: str
    password_hash: str

    role_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "users"