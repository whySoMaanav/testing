import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    
    # Store dynamic fields as JSON for configuration-driven flexibility
    data = Column(Text, nullable=False, default="{}")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    version = relationship("Version", back_populates="risks")

    def get_data(self):
        return json.loads(self.data)

    def set_data(self, data_dict):
        self.data = json.dumps(data_dict)
