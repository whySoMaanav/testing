import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
    
    # Store dynamic fields as JSON for configuration-driven flexibility
    data = Column(Text, nullable=False, default="{}")
    
    # Auth
    access_code_hash = Column(String, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = relationship("Version", back_populates="project", cascade="all, delete-orphan")

    def get_data(self):
        return json.loads(self.data)

    def set_data(self, data_dict):
        self.data = json.dumps(data_dict)
