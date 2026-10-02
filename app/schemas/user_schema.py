from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile_no: str
    password: str = ""
    role_id: int