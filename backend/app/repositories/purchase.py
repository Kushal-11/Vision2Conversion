from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.database import PurchaseModel
from app.models.schemas import PurchaseCreate
import logging

logger = logging.getLogger(__name__)


class PurchaseRepository(BaseRepository[PurchaseModel]):
    """Repository for Purchase operations"""
    
    def __init__(self):
        super().__init__(PurchaseModel)
    
    def create_purchase(self, db: Session, purchase: PurchaseCreate) -> PurchaseModel:
        """Create a new purchase"""
        purchase_data = {
            "user_id": purchase.user_id,
            "product_id": purchase.product_id,
            "amount": purchase.amount,
            "quantity": purchase.quantity,
            "extra_data": purchase.metadata
        }
        return self.create(db, purchase_data)
    
    def get_by_user_id(self, db: Session, user_id: str, limit: int = 100) -> List[PurchaseModel]:
        """Get all purchases for a user"""
        try:
            return (
                db.query(PurchaseModel)
                .filter(PurchaseModel.user_id == user_id)
                .order_by(desc(PurchaseModel.timestamp))
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting purchases for user {user_id}: {e}")
            raise
    
    def get_by_product_id(self, db: Session, product_id: str, limit: int = 100) -> List[PurchaseModel]:
        """Get all purchases for a product"""
        try:
            return (
                db.query(PurchaseModel)
                .filter(PurchaseModel.product_id == product_id)
                .order_by(desc(PurchaseModel.timestamp))
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting purchases for product {product_id}: {e}")
            raise
    
    def get_user_total_spent(self, db: Session, user_id: str) -> float:
        """Get total amount spent by a user"""
        try:
            from sqlalchemy import func
            result = (
                db.query(func.sum(PurchaseModel.amount))
                .filter(PurchaseModel.user_id == user_id)
                .scalar()
            )
            return float(result) if result else 0.0
        except SQLAlchemyError as e:
            logger.error(f"Error calculating total spent for user {user_id}: {e}")
            raise
    
    def get_recent_purchases(self, db: Session, days: int = 30, limit: int = 100) -> List[PurchaseModel]:
        """Get recent purchases within specified days"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return (
                db.query(PurchaseModel)
                .filter(PurchaseModel.timestamp >= cutoff_date)
                .order_by(desc(PurchaseModel.timestamp))
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent purchases: {e}")
            raise


# Create repository instance
purchase_repository = PurchaseRepository()