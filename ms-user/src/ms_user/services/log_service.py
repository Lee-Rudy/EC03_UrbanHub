from src.ms_user.domain.log import Log

class LogService:

    def __init__(self, db):
        self.db = db

    def log_action(self, user_id: str, action: str, resource: str):
        log = Log(
            user_id=user_id,
            action=action,
            resource=resource
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log
