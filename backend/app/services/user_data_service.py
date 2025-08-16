from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.user import user_repository
from app.repositories.purchase import purchase_repository
from app.models.schemas import (
    User, UserCreate, Purchase, PurchaseCreate, 
    UserInterest, UserInterestCreate, UserDataIngestion
)
from app.core.validation import (
    validate_user_data, validate_purchase_data, 
    validate_interest_data, ValidationError
)
import logging

logger = logging.getLogger(__name__)


class UserDataService:
    """Service for managing user data operations"""
    
    def __init__(self):
        self.user_repo = user_repository
        self.purchase_repo = purchase_repository
    
    def create_user(self, db: Session, user_data: Dict[str, Any]) -> User:
        """Create a new user with validation"""
        try:
            # Validate user data
            validated_user = validate_user_data(user_data)
            
            # Check if user already exists
            existing_user = self.user_repo.get_by_email(db, validated_user.email)
            if existing_user:
                raise ValidationError(f"User with email {validated_user.email} already exists")
            
            # Create user
            db_user = self.user_repo.create_user(db, validated_user)
            logger.info(f"Created user: {db_user.email}")
            
            return User.model_validate(db_user)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            db_user = self.user_repo.get_by_id(db, user_id)
            if not db_user:
                return None
            return User.model_validate(db_user)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            db_user = self.user_repo.get_by_email(db, email)
            if not db_user:
                return None
            return User.model_validate(db_user)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    def update_user_profile(self, db: Session, user_id: str, profile_data: Dict[str, Any]) -> Optional[User]:
        """Update user profile data"""
        try:
            db_user = self.user_repo.update_profile_data(db, user_id, profile_data)
            if not db_user:
                return None
            
            logger.info(f"Updated profile for user: {user_id}")
            return User.model_validate(db_user)
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            raise
    
    def add_purchase(self, db: Session, user_id: str, purchase_data: Dict[str, Any]) -> Purchase:
        """Add a purchase for a user"""
        try:
            # Validate purchase data
            purchase_data["user_id"] = user_id
            validated_purchase = validate_purchase_data(purchase_data)
            
            # Verify user exists
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValidationError(f"User with ID {user_id} not found")
            
            # Create purchase
            db_purchase = self.purchase_repo.create_purchase(db, validated_purchase)
            logger.info(f"Added purchase for user {user_id}: ${db_purchase.amount}")
            
            return Purchase.model_validate(db_purchase)
        except Exception as e:
            logger.error(f"Error adding purchase for user {user_id}: {e}")
            raise
    
    def get_user_purchases(self, db: Session, user_id: str, limit: int = 100) -> List[Purchase]:
        """Get all purchases for a user"""
        try:
            db_purchases = self.purchase_repo.get_by_user_id(db, user_id, limit)
            return [Purchase.model_validate(p) for p in db_purchases]
        except Exception as e:
            logger.error(f"Error getting purchases for user {user_id}: {e}")
            raise
    
    def get_user_spending_summary(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get spending summary for a user"""
        try:
            total_spent = self.purchase_repo.get_user_total_spent(db, user_id)
            purchases = self.get_user_purchases(db, user_id)
            
            return {
                "user_id": user_id,
                "total_spent": total_spent,
                "total_purchases": len(purchases),
                "average_purchase": total_spent / len(purchases) if purchases else 0,
                "recent_purchases": purchases[:5]  # Last 5 purchases
            }
        except Exception as e:
            logger.error(f"Error getting spending summary for user {user_id}: {e}")
            raise
    
    def ingest_bulk_user_data(self, db: Session, bulk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest bulk user data (user + purchases + interests)"""
        try:
            # Validate bulk data
            validated_data = UserDataIngestion(**bulk_data)
            
            # Create or get user
            user = self.create_user(db, validated_data.user.dict())
            
            # Add purchases
            created_purchases = []
            for purchase_data in validated_data.purchases:
                purchase_data.user_id = user.id
                purchase = self.add_purchase(db, user.id, purchase_data.dict())
                created_purchases.append(purchase)
            
            # TODO: Add interests when UserInterest repository is implemented
            
            logger.info(f"Bulk ingestion completed for user {user.email}: {len(created_purchases)} purchases")
            
            return {
                "user": user,
                "purchases_created": len(created_purchases),
                "interests_created": 0,  # TODO: Implement when ready
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error during bulk data ingestion: {e}")
            raise


# Create service instance
user_data_service = UserDataService()