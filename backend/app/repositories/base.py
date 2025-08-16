from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, db: Session, obj_data: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        try:
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            db.rollback()
            raise
    
    def get_by_id(self, db: Session, id: str) -> Optional[ModelType]:
        """Get record by ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            raise
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination"""
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise
    
    def update(self, db: Session, id: str, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record"""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return None
            
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id: {id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            db.rollback()
            raise
    
    def delete(self, db: Session, id: str) -> bool:
        """Delete a record"""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return False
            
            db.delete(db_obj)
            db.commit()
            logger.info(f"Deleted {self.model.__name__} with id: {id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            db.rollback()
            raise
    
    def count(self, db: Session) -> int:
        """Count total records"""
        try:
            return db.query(self.model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise