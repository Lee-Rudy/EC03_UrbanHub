from fastapi import Depends, Header, HTTPException
from src.ms_user.domain.role import Role

def get_current_user(x_role: str = Header(default="USER")):
    return {
        "sub": "auth123",
        "role": x_role
    }

def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admins only")
