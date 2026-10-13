from app.database.connection import engine
from app.models.base import Base
# Import all models so Base knows about them
from app.models.project import Project
from app.models.version import Version
from app.models.risk import Risk
from app.models.audit import AuditLog

def init_db():
    Base.metadata.create_all(bind=engine)
