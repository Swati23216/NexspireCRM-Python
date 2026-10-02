from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    role_name: str
    permissions: Optional[list[str]] = None