from sqlalchemy.orm import Session
from app.models.version import Version

class VersionRepository:
    @staticmethod
    def create(db: Session, version: Version) -> Version:
        db.add(version)
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def get_by_id(db: Session, id: int) -> Version:
        return db.query(Version).filter(Version.id == id).first()

    @staticmethod
    def get_by_project_id(db: Session, project_id: int):
        return db.query(Version).filter(Version.project_id == project_id).all()

    @staticmethod
    def update(db: Session, version: Version) -> Version:
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def delete(db: Session, version: Version):
        db.delete(version)
        db.commit()
