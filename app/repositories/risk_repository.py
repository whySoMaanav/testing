from sqlalchemy.orm import Session
from app.models.risk import Risk

class RiskRepository:
    @staticmethod
    def create(db: Session, risk: Risk) -> Risk:
        db.add(risk)
        db.commit()
        db.refresh(risk)
        return risk

    @staticmethod
    def get_by_id(db: Session, id: int) -> Risk:
        return db.query(Risk).filter(Risk.id == id).first()

    @staticmethod
    def get_by_version_id(db: Session, version_id: int):
        return db.query(Risk).filter(Risk.version_id == version_id).all()

    @staticmethod
    def update(db: Session, risk: Risk) -> Risk:
        db.commit()
        db.refresh(risk)
        return risk

    @staticmethod
    def delete(db: Session, risk: Risk):
        db.delete(risk)
        db.commit()
