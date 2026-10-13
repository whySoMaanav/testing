from sqlalchemy.orm import Session
from app.models.project import Project

class ProjectRepository:
    @staticmethod
    def create(db: Session, project: Project) -> Project:
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_by_project_id(db: Session, project_id: str) -> Project:
        return db.query(Project).filter(Project.project_id == project_id).first()
        
    @staticmethod
    def get_by_id(db: Session, id: int) -> Project:
        return db.query(Project).filter(Project.id == id).first()

    @staticmethod
    def get_all(db: Session):
        return db.query(Project).all()

    @staticmethod
    def update(db: Session, project: Project) -> Project:
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete(db: Session, project: Project):
        db.delete(project)
        db.commit()
