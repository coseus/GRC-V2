from sqlalchemy import select
from app.db.models import AuditLog

class AuditRepository:
    def __init__(self, session):
        self.session = session

    def create(self, **kwargs):
        obj = AuditLog(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj

    def list_recent(self, limit: int = 100):
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars())
