from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.services.audit_service import AuditService
from app.utils.auth import generate_access_code, hash_access_code, verify_access_code

class ProjectService:
    @staticmethod
    def create_project(db: Session, project_id: str, data: dict, user: str):
        # Generate access code
        access_code = generate_access_code()
        hashed_code = hash_access_code(access_code)
        
        from app.services.version_service import VersionService
        from datetime import datetime
        
        project = Project(
            project_id=project_id,
            access_code_hash=hashed_code
        )
        project.set_data(data)
        
        created_project = ProjectRepository.create(db, project)
        
        AuditService.log_action(db, user, "Project Created", "Project", created_project.project_id, None, data)
        
        # Auto-create initial version 1.0.0
        initial_version_data = {
            "version_number": "1.0.0",
            "release_date": datetime.utcnow().date().strftime("%Y-%m-%d"),
            "change_summary": "Initial Project Version",
            "submitted_by": data.get("owner", user)
        }
        VersionService.create_version(db, created_project.project_id, initial_version_data, user, is_admin=True)
        
        return created_project, access_code

    @staticmethod
    def authenticate_project(db: Session, project_id: str, access_code: str) -> bool:
        project = ProjectRepository.get_by_project_id(db, project_id)
        if not project:
            return False
        return verify_access_code(access_code, project.access_code_hash)

    @staticmethod
    def update_project(db: Session, project_id: str, new_data: dict, user: str, is_admin: bool = False, auth_project_id: str = None):
        if not is_admin and auth_project_id != project_id:
            raise PermissionError("Not authorized to edit this project.")
            
        project = ProjectRepository.get_by_project_id(db, project_id)
        if not project:
            raise ValueError("Project not found.")
            
        old_data = project.get_data()
        project.set_data(new_data)
        updated_project = ProjectRepository.update(db, project)
        
        AuditService.log_action(db, user, "Project Updated", "Project", project_id, old_data, new_data)
        return updated_project

    @staticmethod
    def get_all_projects(db: Session):
        return ProjectRepository.get_all(db)

    @staticmethod
    def get_project(db: Session, project_id: str):
        return ProjectRepository.get_by_project_id(db, project_id)

    @staticmethod
    def regenerate_access_code(db: Session, project_id: str, user: str, is_admin: bool = False):
        if not is_admin:
            raise PermissionError("Only administrators can regenerate access codes.")
            
        project = ProjectRepository.get_by_project_id(db, project_id)
        if not project:
            raise ValueError("Project not found.")
            
        new_code = generate_access_code()
        hashed_code = hash_access_code(new_code)
        
        project.access_code_hash = hashed_code
        ProjectRepository.update(db, project)
        
        AuditService.log_action(db, user, "Access Code Regenerated", "Project", project_id, None, None)
        
        return new_code
