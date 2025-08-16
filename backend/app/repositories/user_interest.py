from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base import BaseRepository
from app.models.database import UserInterestModel
from app.models.schemas import UserInterestCreate, InterestCategory
import logging

logger = logging.getLogger(__name__)


class UserInterestRepository(BaseRepository[UserInterestModel]):
    """Repository for UserInterest operations"""
    
    def __init__(self):
        super().__init__(UserInterestModel)
    
    def get_by_user_id(self, db: Session, user_id: str, limit: int = 100) -> List[UserInterestModel]:
        """Get all interests for a user"""
        try:
            return (
                db.query(UserInterestModel)
                .filter(UserInterestModel.user_id == user_id)
                .order_by(UserInterestModel.confidence_score.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting interests for user {user_id}: {e}")
            raise
    
    def get_by_category(self, db: Session, user_id: str, category: InterestCategory) -> List[UserInterestModel]:
        """Get user interests by category"""
        try:
            return (
                db.query(UserInterestModel)
                .filter(
                    UserInterestModel.user_id == user_id,
                    UserInterestModel.interest_category == category.value
                )
                .order_by(UserInterestModel.confidence_score.desc())
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting interests for user {user_id}, category {category}: {e}")
            raise
    
    def get_by_source(self, db: Session, user_id: str, source: str) -> List[UserInterestModel]:
        """Get user interests by source"""
        try:
            return (
                db.query(UserInterestModel)
                .filter(
                    UserInterestModel.user_id == user_id,
                    UserInterestModel.source == source
                )
                .order_by(UserInterestModel.confidence_score.desc())
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting interests for user {user_id}, source {source}: {e}")
            raise
    
    def create_interest(self, db: Session, interest: UserInterestCreate) -> UserInterestModel:
        """Create a new user interest"""
        interest_data = {
            "user_id": interest.user_id,
            "interest_category": interest.interest_category.value,
            "interest_value": interest.interest_value,
            "confidence_score": interest.confidence_score,
            "source": interest.source
        }
        return self.create(db, interest_data)
    
    def update_confidence_score(self, db: Session, interest_id: str, new_score: float) -> Optional[UserInterestModel]:
        """Update confidence score for an interest"""
        try:
            return self.update(db, interest_id, {"confidence_score": new_score})
        except SQLAlchemyError as e:
            logger.error(f"Error updating confidence score for interest {interest_id}: {e}")
            raise
    
    def get_top_interests_by_category(self, db: Session, user_id: str, limit: int = 5) -> List[dict]:
        """Get top interests grouped by category"""
        try:
            from sqlalchemy import func
            result = (
                db.query(
                    UserInterestModel.interest_category,
                    func.avg(UserInterestModel.confidence_score).label("avg_confidence"),
                    func.count(UserInterestModel.id).label("interest_count")
                )
                .filter(UserInterestModel.user_id == user_id)
                .group_by(UserInterestModel.interest_category)
                .order_by(func.avg(UserInterestModel.confidence_score).desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "category": row.interest_category,
                    "avg_confidence": float(row.avg_confidence),
                    "interest_count": row.interest_count
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            logger.error(f"Error getting top interests by category for user {user_id}: {e}")
            raise
    
    def find_duplicate_interest(self, db: Session, user_id: str, category: str, value: str) -> Optional[UserInterestModel]:
        """Find if a similar interest already exists"""
        try:
            return (
                db.query(UserInterestModel)
                .filter(
                    UserInterestModel.user_id == user_id,
                    UserInterestModel.interest_category == category,
                    UserInterestModel.interest_value == value
                )
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error finding duplicate interest: {e}")
            raise


# Create repository instance
user_interest_repository = UserInterestRepository()