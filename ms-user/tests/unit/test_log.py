from src.ms_user.services.log_service import LogService
from src.ms_user.domain.log import Log


class FakeDB:
    def __init__(self):
        self.data = []

    def add(self, obj):
        self.data.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def test_audit_log_creation():
    db = FakeDB()
    service = LogService(db)

    log = service.log_action(
        user_id="user123",
        action="CREATE_USER",
        resource="user"
    )

    assert isinstance(log, Log)
    assert log.user_id == "user123"
    assert log.action == "CREATE_USER"
    assert log.resource == "user"