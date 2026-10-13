import json
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.utils.logger import logger

class AuditService:
    @staticmethod
    def log_action(db: Session, user: str, action: str, entity_type: str, entity_id: str, old_value: dict = None, new_value: dict = None):
        """Log an action to the database."""
        try:
            log_entry = AuditLog(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                old_value=json.dumps(old_value) if old_value else None,
                new_value=json.dumps(new_value) if new_value else None
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to write audit log: {e}")

    @staticmethod
    def get_logs(db: Session, limit: int = 100):
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
