from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base import BaseRepository
from app.models.database import UserModel
from app.models.schemas import UserCreate, User
import logging

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[UserModel]):
    """Repository for User operations"""
    
    def __init__(self):
        super().__init__(UserModel)
    
    def get_by_email(self, db: Session, email: str) -> Optional[UserModel]:
        """Get user by email address"""
        try:
            return db.query(UserModel).filter(UserModel.email == email.lower()).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    def create_user(self, db: Session, user: UserCreate) -> UserModel:
        """Create a new user"""
        user_data = {
            "email": user.email.lower(),
            "profile_data": user.profile_data
        }
        return self.create(db, user_data)
    
    def update_profile_data(self, db: Session, user_id: str, profile_data: dict) -> Optional[UserModel]:
        """Update user profile data"""
        try:
            db_user = self.get_by_id(db, user_id)
            if not db_user:
                return None
            
            # Merge new profile data with existing
            updated_profile = {**db_user.profile_data, **profile_data}
            return self.update(db, user_id, {"profile_data": updated_profile})
        except SQLAlchemyError as e:
            logger.error(f"Error updating profile data for user {user_id}: {e}")
            raise
    
    def search_users(self, db: Session, query: str, limit: int = 10) -> List[UserModel]:
        """Search users by email or profile data"""
        try:
            return (
                db.query(UserModel)
                .filter(UserModel.email.ilike(f"%{query}%"))
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error searching users with query '{query}': {e}")
            raise


# Create repository instance
user_repository = UserRepository()