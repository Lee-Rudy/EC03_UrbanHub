from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.ms_user.repositories.user_repository import UserRepository
from src.ms_user.services.user_service import UserService
from src.ms_user.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserResponseDTO
)

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)


@router.post("/", response_model=UserResponseDTO)
def create_user(dto: UserCreateDTO, service: UserService = Depends(get_service)):
    return service.create_user(dto)


@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(user_id: int, service: UserService = Depends(get_service)):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur Introuvable")
    return user


@router.get("/", response_model=list[UserResponseDTO])
def get_users(service: UserService = Depends(get_service)):
    return service.get_users()


@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(user_id: int, dto: UserUpdateDTO, service: UserService = Depends(get_service)):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur Introuvable")

    return service.update_user(user, dto)


@router.delete("/{user_id}")
def delete_user(user_id: int, service: UserService = Depends(get_service)):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur Introuvable")

    service.delete_user(user)
    return {"message": "deleted"}