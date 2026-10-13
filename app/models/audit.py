from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = Column(String, nullable=False)
    action = Column(String, nullable=False) # e.g., 'Project Created', 'Risk Modified'
    entity_type = Column(String, nullable=False) # e.g., 'Project', 'Version', 'Risk'
    entity_id = Column(String, nullable=False)
    old_value = Column(Text, nullable=True) # JSON string
    new_value = Column(Text, nullable=True) # JSON string
