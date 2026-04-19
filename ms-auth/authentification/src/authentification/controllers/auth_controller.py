from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from authentification.domains.login import Login
from authentification.dtos.login_dto import LoginDTO
from authentification.dtos.token_dto import TokenDTO
from authentification.repositories.database import get_db
from authentification.repositories.token_repository import TokenRepository
from authentification.repositories.user_repository import UserRepository
from authentification.security.jwt_service import JWTService
from authentification.security.password_hasher import BcryptPasswordHasher

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenDTO)
def login(payload: LoginDTO, db: Session = Depends(get_db)) -> TokenDTO:
    """Authentifie un utilisateur et retourne un JWT.

    Règles:
    - valide les champs selon la logique métier (`domains.Login`)
    - cherche l'utilisateur par email
    - vérifie le mot de passe via bcrypt
    - génère un token JWT incluant `sub`, `email`, `role`
    - persiste le token et un log d'action
    """

    try:
        login_data = Login(email=payload.email, password=payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    user_repo = UserRepository(db)
    user = user_repo.get_by_email(login_data.get_email())
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides.")

    hasher = BcryptPasswordHasher()
    if not hasher.verify_password(login_data.get_password(), user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides.")

    jwt_service = JWTService()
    access_token, expires_at = jwt_service.create_access_token(
        subject=str(user.id),
        email=user.email,
        role=user.role.value,
    )

    token_repo = TokenRepository(db)
    token_repo.save_access_token(
        user_id=str(user.id),
        access_token=access_token,
        expires_at=expires_at,
    )
    token_repo.log_action(user_id=str(user.id), action="LOGIN_SUCCESS")

    return TokenDTO(access_token=access_token)

