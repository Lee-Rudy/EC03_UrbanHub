from src.ms_user.domain.user import User
from src.ms_user.domain.role import Role


class FakeDB:
    def __init__(self):
        self.data = []

    def add(self, obj):
        self.data.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def query(self, model):
        return self


def test_user_repository_create():
    db = FakeDB()

    user = User(
        auth_user_id="auth1",
        email="test@mail.com",
        name="John",
        role=Role.USER
    )

    db.add(user)

    assert len(db.data) == 1