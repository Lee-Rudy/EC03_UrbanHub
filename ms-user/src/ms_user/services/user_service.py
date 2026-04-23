from src.ms_user.domain.user import User
from src.ms_user.repositories.user_repository import UserRepository
from src.ms_user.dto.user_dto import UserCreateDTO, UserUpdateDTO

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, dto: UserCreateDTO):
        user = User(
            auth_user_id=dto.auth_user_id,
            email=dto.email,
            name=dto.name,
            role=dto.role
        )
        return self.repo.create(user)

    def get_user(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def get_users(self):
        return self.repo.get_all()

    def update_user(self, user, dto: UserUpdateDTO):
        if dto.email:
            user.email = dto.email
        if dto.name:
            user.name = dto.name
        if dto.role:
            user.role = dto.role
        return self.repo.update(user)

    def delete_user(self, user):
        self.repo.delete(user)