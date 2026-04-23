from pydantic import BaseModel
from typing import Optional
from src.ms_user.domain.role import Role


class UserCreateDTO(BaseModel):
    auth_user_id: str
    email: str
    name: str
    role: Role

class UserUpdateDTO(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[Role] = None

class UserResponseDTO(BaseModel):
    id: int
    auth_user_id: str
    email: str
    name: str
    role: Role

    class Config:
        from_attributes = True