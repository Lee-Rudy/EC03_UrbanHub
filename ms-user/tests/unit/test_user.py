from src.ms_user.domain.user import User

def test_create_user_instance():
    user = User(
        auth_user_id="abc123",
        email="test@mail.com",
        name="John"
    )
    assert user.email == "test@mail.com"
    