from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.repositories.user import user_repository
from app.repositories.purchase import purchase_repository
from app.repositories.user_interest import user_interest_repository
from app.repositories.product import product_repository
from app.models.database import UserModel, PurchaseModel, UserInterestModel, ProductModel
from app.models.schemas import ProductCategory, InterestCategory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and metrics"""
    
    def __init__(self):
        self.user_repo = user_repository
        self.purchase_repo = purchase_repository
        self.interest_repo = user_interest_repository
        self.product_repo = product_repository
    
    def get_platform_overview(self, db: Session) -> Dict[str, Any]:
        """Get high-level platform metrics"""
        try:
            # Basic counts
            total_users = self.user_repo.count(db)
            total_products = self.product_repo.count(db)
            total_purchases = db.query(PurchaseModel).count()
            total_interests = db.query(UserInterestModel).count()
            
            # Revenue metrics
            total_revenue = db.query(func.sum(PurchaseModel.amount)).scalar() or 0
            avg_order_value = db.query(func.avg(PurchaseModel.amount)).scalar() or 0
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_users = db.query(UserModel).filter(UserModel.created_at >= thirty_days_ago).count()
            recent_purchases = db.query(PurchaseModel).filter(PurchaseModel.timestamp >= thirty_days_ago).count()
            recent_revenue = db.query(func.sum(PurchaseModel.amount)).filter(
                PurchaseModel.timestamp >= thirty_days_ago
            ).scalar() or 0
            
            return {
                "overview": {
                    "total_users": total_users,
                    "total_products": total_products,
                    "total_purchases": total_purchases,
                    "total_interests": total_interests,
                    "total_revenue": float(total_revenue),
                    "average_order_value": float(avg_order_value)
                },
                "last_30_days": {
                    "new_users": recent_users,
                    "purchases": recent_purchases,
                    "revenue": float(recent_revenue)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting platform overview: {e}")
            raise
    
    def get_user_analytics(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user"""
        try:
            # User info
            user = self.user_repo.get_by_id(db, user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Purchase analytics
            purchases = db.query(PurchaseModel).filter(PurchaseModel.user_id == user_id).all()
            total_spent = sum(p.amount for p in purchases)
            total_purchases = len(purchases)
            avg_purchase = total_spent / total_purchases if total_purchases > 0 else 0
            
            # Purchase timeline (last 12 months)
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            recent_purchases = db.query(PurchaseModel).filter(
                PurchaseModel.user_id == user_id,
                PurchaseModel.timestamp >= one_year_ago
            ).all()
            
            # Group purchases by month
            monthly_spending = {}
            for purchase in recent_purchases:
                month_key = purchase.timestamp.strftime("%Y-%m")
                monthly_spending[month_key] = monthly_spending.get(month_key, 0) + purchase.amount
            
            # Interest analytics
            interests = db.query(UserInterestModel).filter(UserInterestModel.user_id == user_id).all()
            interest_categories = {}
            for interest in interests:
                category = interest.interest_category
                if category not in interest_categories:
                    interest_categories[category] = {
                        "count": 0,
                        "avg_confidence": 0,
                        "interests": []
                    }
                interest_categories[category]["count"] += 1
                interest_categories[category]["interests"].append({
                    "value": interest.interest_value,
                    "confidence": interest.confidence_score,
                    "source": interest.source
                })
            
            # Calculate average confidence per category
            for category_data in interest_categories.values():
                total_confidence = sum(i["confidence"] for i in category_data["interests"])
                category_data["avg_confidence"] = total_confidence / category_data["count"]
            
            return {
                "user_id": user_id,
                "email": user.email,
                "member_since": user.created_at.isoformat(),
                "purchase_analytics": {
                    "total_spent": float(total_spent),
                    "total_purchases": total_purchases,
                    "average_purchase": float(avg_purchase),
                    "monthly_spending": {k: float(v) for k, v in monthly_spending.items()}
                },
                "interest_analytics": interest_categories,
                "activity_summary": {
                    "last_purchase": max([p.timestamp for p in purchases]).isoformat() if purchases else None,
                    "most_recent_interest": max([i.created_at for i in interests]).isoformat() if interests else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting user analytics for {user_id}: {e}")
            raise
    
    def get_product_analytics(self, db: Session, limit: int = 100) -> Dict[str, Any]:
        """Get product performance analytics"""
        try:
            # Most purchased products
            popular_products = (
                db.query(
                    PurchaseModel.product_id,
                    func.count(PurchaseModel.id).label("purchase_count"),
                    func.sum(PurchaseModel.amount).label("total_revenue"),
                    func.avg(PurchaseModel.amount).label("avg_price")
                )
                .group_by(PurchaseModel.product_id)
                .order_by(desc(func.count(PurchaseModel.id)))
                .limit(limit)
                .all()
            )
            
            # Category performance
            category_performance = (
                db.query(ProductModel.category)
                .join(PurchaseModel, ProductModel.id == PurchaseModel.product_id)
                .group_by(ProductModel.category)
                .with_entities(
                    ProductModel.category,
                    func.count(PurchaseModel.id).label("total_purchases"),
                    func.sum(PurchaseModel.amount).label("total_revenue"),
                    func.count(func.distinct(ProductModel.id)).label("unique_products"),
                    func.count(func.distinct(PurchaseModel.user_id)).label("unique_customers")
                )
                .order_by(desc(func.sum(PurchaseModel.amount)))
                .all()
            )
            
            # Price distribution
            price_ranges = {
                "0-25": 0, "25-50": 0, "50-100": 0, "100-250": 0, "250+": 0
            }
            
            products = db.query(ProductModel).all()
            for product in products:
                if product.price <= 25:
                    price_ranges["0-25"] += 1
                elif product.price <= 50:
                    price_ranges["25-50"] += 1
                elif product.price <= 100:
                    price_ranges["50-100"] += 1
                elif product.price <= 250:
                    price_ranges["100-250"] += 1
                else:
                    price_ranges["250+"] += 1
            
            return {
                "popular_products": [
                    {
                        "product_id": p.product_id,
                        "purchase_count": p.purchase_count,
                        "total_revenue": float(p.total_revenue),
                        "avg_price": float(p.avg_price)
                    }
                    for p in popular_products
                ],
                "category_performance": [
                    {
                        "category": cp.category,
                        "total_purchases": cp.total_purchases,
                        "total_revenue": float(cp.total_revenue),
                        "unique_products": cp.unique_products,
                        "unique_customers": cp.unique_customers
                    }
                    for cp in category_performance
                ],
                "price_distribution": price_ranges,
                "total_products": len(products)
            }
        except Exception as e:
            logger.error(f"Error getting product analytics: {e}")
            raise
    
    def get_interest_analytics(self, db: Session) -> Dict[str, Any]:
        """Get interest and recommendation analytics"""
        try:
            # Interest category distribution
            category_stats = (
                db.query(UserInterestModel.interest_category)
                .group_by(UserInterestModel.interest_category)
                .with_entities(
                    UserInterestModel.interest_category,
                    func.count(UserInterestModel.id).label("total_interests"),
                    func.avg(UserInterestModel.confidence_score).label("avg_confidence"),
                    func.count(func.distinct(UserInterestModel.user_id)).label("unique_users")
                )
                .order_by(desc(func.count(UserInterestModel.id)))
                .all()
            )
            
            # Interest sources
            source_stats = (
                db.query(UserInterestModel.source)
                .group_by(UserInterestModel.source)
                .with_entities(
                    UserInterestModel.source,
                    func.count(UserInterestModel.id).label("total_interests"),
                    func.avg(UserInterestModel.confidence_score).label("avg_confidence")
                )
                .order_by(desc(func.count(UserInterestModel.id)))
                .all()
            )
            
            # Top interest values by category
            top_interests = {}
            for category in InterestCategory:
                top_in_category = (
                    db.query(UserInterestModel.interest_value)
                    .filter(UserInterestModel.interest_category == category.value)
                    .group_by(UserInterestModel.interest_value)
                    .with_entities(
                        UserInterestModel.interest_value,
                        func.count(UserInterestModel.id).label("count"),
                        func.avg(UserInterestModel.confidence_score).label("avg_confidence")
                    )
                    .order_by(desc(func.count(UserInterestModel.id)))
                    .limit(5)
                    .all()
                )
                
                top_interests[category.value] = [
                    {
                        "value": ti.interest_value,
                        "count": ti.count,
                        "avg_confidence": float(ti.avg_confidence)
                    }
                    for ti in top_in_category
                ]
            
            return {
                "category_distribution": [
                    {
                        "category": cs.interest_category,
                        "total_interests": cs.total_interests,
                        "avg_confidence": float(cs.avg_confidence),
                        "unique_users": cs.unique_users
                    }
                    for cs in category_stats
                ],
                "source_distribution": [
                    {
                        "source": ss.source,
                        "total_interests": ss.total_interests,
                        "avg_confidence": float(ss.avg_confidence)
                    }
                    for ss in source_stats
                ],
                "top_interests_by_category": top_interests
            }
        except Exception as e:
            logger.error(f"Error getting interest analytics: {e}")
            raise
    
    def get_revenue_analytics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics for specified time period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Daily revenue
            daily_revenue = (
                db.query(
                    func.date(PurchaseModel.timestamp).label("date"),
                    func.sum(PurchaseModel.amount).label("revenue"),
                    func.count(PurchaseModel.id).label("transactions")
                )
                .filter(PurchaseModel.timestamp >= start_date)
                .group_by(func.date(PurchaseModel.timestamp))
                .order_by(func.date(PurchaseModel.timestamp))
                .all()
            )
            
            # Revenue by category
            category_revenue = (
                db.query(ProductModel.category)
                .join(PurchaseModel, ProductModel.id == PurchaseModel.product_id)
                .filter(PurchaseModel.timestamp >= start_date)
                .group_by(ProductModel.category)
                .with_entities(
                    ProductModel.category,
                    func.sum(PurchaseModel.amount).label("revenue"),
                    func.count(PurchaseModel.id).label("transactions")
                )
                .order_by(desc(func.sum(PurchaseModel.amount)))
                .all()
            )
            
            # Top customers by spending
            top_customers = (
                db.query(PurchaseModel.user_id)
                .filter(PurchaseModel.timestamp >= start_date)
                .group_by(PurchaseModel.user_id)
                .with_entities(
                    PurchaseModel.user_id,
                    func.sum(PurchaseModel.amount).label("total_spent"),
                    func.count(PurchaseModel.id).label("purchases")
                )
                .order_by(desc(func.sum(PurchaseModel.amount)))
                .limit(10)
                .all()
            )
            
            return {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "daily_revenue": [
                    {
                        "date": dr.date.isoformat(),
                        "revenue": float(dr.revenue),
                        "transactions": dr.transactions
                    }
                    for dr in daily_revenue
                ],
                "category_revenue": [
                    {
                        "category": cr.category,
                        "revenue": float(cr.revenue),
                        "transactions": cr.transactions
                    }
                    for cr in category_revenue
                ],
                "top_customers": [
                    {
                        "user_id": tc.user_id,
                        "total_spent": float(tc.total_spent),
                        "purchases": tc.purchases
                    }
                    for tc in top_customers
                ]
            }
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            raise


# Create service instance
analytics_service = AnalyticsService()