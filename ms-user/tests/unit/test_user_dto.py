import pytest
from src.ms_user.dto.user_dto import UserCreateDTO
from src.ms_user.domain.role import Role


def test_user_create_dto_valid():
    dto = UserCreateDTO(
        auth_user_id="auth123",
        email="test@mail.com",
        name="John",
        role=Role.USER
    )

    assert dto.email == "test@mail.com"
    assert dto.role == Role.USER