from src.ms_user.services.user_service import UserService
from src.ms_user.dto.user_dto import UserCreateDTO, UserUpdateDTO
from src.ms_user.domain.role import Role
from src.ms_user.domain.user import User


# Fake repository (important pour unit test)
class FakeRepo:

    def __init__(self):
        self.users = {}

    def create(self, user):
        user.id = 1
        self.users[user.id] = user
        return user

    def get_by_id(self, user_id):
        return self.users.get(user_id)

    def get_all(self):
        return list(self.users.values())

    def update(self, user):
        self.users[user.id] = user
        return user

    def delete(self, user):
        self.users.pop(user.id, None)


def test_create_user_service():
    repo = FakeRepo()
    service = UserService(repo)

    dto = UserCreateDTO(
        auth_user_id="auth123",
        email="test@mail.com",
        name="John",
        role=Role.USER
    )

    user = service.create_user(dto)

    assert user.email == "test@mail.com"
    assert user.role == Role.USER


def test_update_user_service():
    repo = FakeRepo()
    service = UserService(repo)

    user = service.create_user(
        UserCreateDTO(
            auth_user_id="auth123",
            email="old@mail.com",
            name="John",
            role=Role.USER
        )
    )

    dto = UserUpdateDTO(email="new@mail.com")

    updated = service.update_user(user, dto)

    assert updated.email == "new@mail.com"