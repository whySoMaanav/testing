from sqlalchemy.orm import Session
from app.models.version import Version
from app.repositories.version_repository import VersionRepository
from app.repositories.project_repository import ProjectRepository
from app.services.audit_service import AuditService

class VersionService:
    @staticmethod
    def create_version(db: Session, project_id: str, data: dict, user: str, is_admin: bool = False, auth_project_id: str = None):
        if not is_admin and auth_project_id != project_id:
            raise PermissionError("Not authorized to add versions to this project.")
            
        project = ProjectRepository.get_by_project_id(db, project_id)
        if not project:
            raise ValueError("Project not found.")
            
        version = Version(project_id=project.id)
        version.set_data(data)
        
        created_version = VersionRepository.create(db, version)
        
        AuditService.log_action(db, user, "Version Added", "Version", str(created_version.id), None, data)
        return created_version

    @staticmethod
    def update_version(db: Session, version_id: int, new_data: dict, user: str, is_admin: bool = False, auth_project_id: str = None):
        version = VersionRepository.get_by_id(db, version_id)
        if not version:
            raise ValueError("Version not found.")
            
        if not is_admin and auth_project_id != version.project.project_id:
            raise PermissionError("Not authorized to edit this version.")
            
        old_data = version.get_data()
        version.set_data(new_data)
        updated_version = VersionRepository.update(db, version)
        
        AuditService.log_action(db, user, "Version Updated", "Version", str(version_id), old_data, new_data)
        return updated_version

    @staticmethod
    def get_versions_for_project(db: Session, project_id_str: str):
        project = ProjectRepository.get_by_project_id(db, project_id_str)
        if not project:
            return []
        return VersionRepository.get_by_project_id(db, project.id)

    @staticmethod
    def delete_version(db: Session, version_id: int, user: str, is_admin: bool = False):
        if not is_admin:
            raise PermissionError("Only administrators can delete versions.")
            
        version = VersionRepository.get_by_id(db, version_id)
        if not version:
            raise ValueError("Version not found.")
            
        old_data = version.get_data()
        VersionRepository.delete(db, version)
        
        AuditService.log_action(db, user, "Version Deleted", "Version", str(version_id), old_data, None)
