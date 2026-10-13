import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Store dynamic fields as JSON for configuration-driven flexibility
    data = Column(Text, nullable=False, default="{}")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="versions")
    risks = relationship("Risk", back_populates="version", cascade="all, delete-orphan")

    def get_data(self):
        return json.loads(self.data)

    def set_data(self, data_dict):
        self.data = json.dumps(data_dict)
