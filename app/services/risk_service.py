from sqlalchemy.orm import Session
from app.models.risk import Risk
from app.repositories.risk_repository import RiskRepository
from app.repositories.version_repository import VersionRepository
from app.services.audit_service import AuditService
from app.utils.risk_matrix import calculate_risk

class RiskService:
    @staticmethod
    def add_risk(db: Session, version_id: int, data: dict, user: str, is_admin: bool = False, auth_project_id: str = None):
        version = VersionRepository.get_by_id(db, version_id)
        if not version:
            raise ValueError("Version not found.")
            
        if not is_admin and auth_project_id != version.project.project_id:
            raise PermissionError("Not authorized to add risks to this version.")
            
        # Automatically compute risk score and level if likelihood & impact provided
        if 'likelihood' in data or 'impact' in data:
            risk_calc = calculate_risk(data.get('likelihood'), data.get('impact'))
            if risk_calc['score'] is not None:
                data['risk_score'] = risk_calc['score']
                data['risk_level'] = risk_calc['level']
                data['risk_score_label'] = risk_calc['label']

        risk = Risk(version_id=version_id)
        risk.set_data(data)
        
        created_risk = RiskRepository.create(db, risk)
        
        AuditService.log_action(db, user, "Risk Added", "Risk", str(created_risk.id), None, data)
        return created_risk

    @staticmethod
    def update_risk(db: Session, risk_id: int, new_data: dict, user: str, is_admin: bool = False, auth_project_id: str = None):
        risk = RiskRepository.get_by_id(db, risk_id)
        if not risk:
            raise ValueError("Risk not found.")
            
        if not is_admin and auth_project_id != risk.version.project.project_id:
            raise PermissionError("Not authorized to edit this risk.")
            
        old_data = risk.get_data()
        
        # Automatically compute risk score and level if likelihood & impact provided
        if 'likelihood' in new_data or 'impact' in new_data:
            risk_calc = calculate_risk(new_data.get('likelihood'), new_data.get('impact'))
            if risk_calc['score'] is not None:
                new_data['risk_score'] = risk_calc['score']
                new_data['risk_level'] = risk_calc['level']
                new_data['risk_score_label'] = risk_calc['label']

        risk.set_data(new_data)
        updated_risk = RiskRepository.update(db, risk)
        
        AuditService.log_action(db, user, "Risk Updated", "Risk", str(risk_id), old_data, new_data)
        return updated_risk

    @staticmethod
    def get_risks_for_version(db: Session, version_id: int):
        return RiskRepository.get_by_version_id(db, version_id)
