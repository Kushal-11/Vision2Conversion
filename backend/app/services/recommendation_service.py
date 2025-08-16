from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.product_service import product_service
from app.services.user_data_service import user_data_service
from app.services.cache_service import cache_service
from app.models.schemas import Recommendation, ProductCategory, User, Product
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating personalized product recommendations"""
    
    def __init__(self):
        self.kg_service = knowledge_graph_service
        self.product_service = product_service
        self.user_service = user_data_service
        self.cache_service = cache_service
    
    def get_personalized_recommendations(
        self, 
        db: Session, 
        user_id: str, 
        limit: int = 10
    ) -> List[Recommendation]:
        """Get personalized recommendations for a user"""
        try:
            # Check cache first
            cached_recommendations = self.cache_service.get_user_recommendations(user_id)
            if cached_recommendations:
                logger.info(f"Returning cached recommendations for user {user_id}")
                return [Recommendation(**rec) for rec in cached_recommendations[:limit]]
            
            # Verify user exists
            user = self.user_service.get_user_by_id(db, user_id)
            if not user:
                logger.warning(f"User {user_id} not found for recommendations")
                return []
            
            # Get recommendations from knowledge graph
            kg_recommendations = self.kg_service.get_user_recommendations(user_id, limit)
            
            # Convert to recommendation objects and validate products exist
            recommendations = []
            for rec_data in kg_recommendations:
                product = self.product_service.get_product_by_id(db, rec_data["product_id"])
                if product:
                    try:
                        category = ProductCategory(rec_data["category"])
                        recommendation = Recommendation(
                            product_id=rec_data["product_id"],
                            score=rec_data["score"],
                            reason=rec_data["reason"],
                            category=category
                        )
                        recommendations.append(recommendation)
                    except ValueError:
                        logger.warning(f"Invalid category {rec_data['category']} for product {rec_data['product_id']}")
                        continue
            
            # If we don't have enough recommendations from KG, fill with popular products
            if len(recommendations) < limit:
                fallback_recommendations = self._get_fallback_recommendations(
                    db, user_id, limit - len(recommendations)
                )
                recommendations.extend(fallback_recommendations)
            
            # Cache the results
            recommendations_to_cache = [rec.dict() for rec in recommendations[:limit]]
            self.cache_service.cache_user_recommendations(user_id, recommendations_to_cache)
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations[:limit]
        
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return self._get_fallback_recommendations(db, user_id, limit)
    
    def get_category_recommendations(
        self, 
        db: Session, 
        user_id: str, 
        category: ProductCategory, 
        limit: int = 10
    ) -> List[Recommendation]:
        """Get recommendations within a specific category"""
        try:
            # Check cache first
            cached_recommendations = self.cache_service.get_category_recommendations(user_id, category.value)
            if cached_recommendations:
                logger.info(f"Returning cached category recommendations for user {user_id}, category {category}")
                return [Recommendation(**rec) for rec in cached_recommendations[:limit]]
            
            # Get user's purchase history in this category
            user_purchases = self.user_service.get_user_purchases(db, user_id)
            purchased_products = {p.product_id for p in user_purchases}
            
            # Get products in category
            category_products = self.product_service.get_products_by_category(db, category, limit * 2)
            
            # Filter out already purchased products
            available_products = [p for p in category_products if p.id not in purchased_products]
            
            recommendations = []
            for product in available_products[:limit]:
                recommendation = Recommendation(
                    product_id=product.id,
                    score=0.8,  # Default score for category-based recommendations
                    reason=f"Popular product in {category.value} category",
                    category=category
                )
                recommendations.append(recommendation)
            
            # Cache the results
            recommendations_to_cache = [rec.dict() for rec in recommendations]
            self.cache_service.cache_category_recommendations(user_id, category.value, recommendations_to_cache)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating category recommendations for user {user_id}, category {category}: {e}")
            return []
    
    def get_trending_recommendations(self, db: Session, limit: int = 10) -> List[Recommendation]:
        """Get trending product recommendations"""
        try:
            # Check cache first
            cached_trending = self.cache_service.get_trending_products()
            if cached_trending:
                logger.info("Returning cached trending recommendations")
                return [Recommendation(**rec) for rec in cached_trending[:limit]]
            
            trending_data = self.kg_service.get_trending_products(limit)
            
            recommendations = []
            for trend_data in trending_data:
                product = self.product_service.get_product_by_id(db, trend_data["product_id"])
                if product:
                    try:
                        category = ProductCategory(trend_data["category"])
                        score = min(trend_data["trend_score"] / 100.0, 1.0)  # Normalize score
                        recommendation = Recommendation(
                            product_id=trend_data["product_id"],
                            score=score,
                            reason=f"Trending: {trend_data['purchase_count']} recent purchases",
                            category=category
                        )
                        recommendations.append(recommendation)
                    except ValueError:
                        logger.warning(f"Invalid category {trend_data['category']} for trending product")
                        continue
            
            # Cache the results
            recommendations_to_cache = [rec.dict() for rec in recommendations]
            self.cache_service.cache_trending_products(recommendations_to_cache)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {e}")
            return []
    
    def get_similar_user_recommendations(
        self, 
        db: Session, 
        user_id: str, 
        limit: int = 10
    ) -> List[Recommendation]:
        """Get recommendations based on similar users' purchases"""
        try:
            similar_users = self.kg_service.get_similar_users(user_id, 5)
            if not similar_users:
                return []
            
            # Get current user's purchases to avoid recommending already purchased items
            user_purchases = self.user_service.get_user_purchases(db, user_id)
            purchased_products = {p.product_id for p in user_purchases}
            
            recommendations = []
            for similar_user in similar_users:
                similar_user_purchases = self.user_service.get_user_purchases(
                    db, similar_user["user_id"], 20
                )
                
                for purchase in similar_user_purchases:
                    if purchase.product_id not in purchased_products:
                        product = self.product_service.get_product_by_id(db, purchase.product_id)
                        if product:
                            try:
                                category = ProductCategory(product.category.value)
                                recommendation = Recommendation(
                                    product_id=purchase.product_id,
                                    score=similar_user["similarity_score"] * 0.8,
                                    reason=f"Users with similar tastes also bought this",
                                    category=category
                                )
                                recommendations.append(recommendation)
                                
                                if len(recommendations) >= limit:
                                    break
                            except ValueError:
                                continue
                
                if len(recommendations) >= limit:
                    break
            
            return recommendations[:limit]
        
        except Exception as e:
            logger.error(f"Error getting similar user recommendations for {user_id}: {e}")
            return []
    
    def _get_fallback_recommendations(
        self, 
        db: Session, 
        user_id: str, 
        limit: int
    ) -> List[Recommendation]:
        """Get fallback recommendations when personalized ones aren't available"""
        try:
            # Get featured/popular products as fallback
            featured_products = self.product_service.get_featured_products(db, limit)
            
            # Get user's purchases to avoid recommending already purchased items
            user_purchases = self.user_service.get_user_purchases(db, user_id)
            purchased_products = {p.product_id for p in user_purchases}
            
            recommendations = []
            for product in featured_products:
                if product.id not in purchased_products:
                    recommendation = Recommendation(
                        product_id=product.id,
                        score=0.5,  # Lower score for fallback recommendations
                        reason="Popular product recommendation",
                        category=product.category
                    )
                    recommendations.append(recommendation)
            
            return recommendations[:limit]
        
        except Exception as e:
            logger.error(f"Error getting fallback recommendations: {e}")
            return []
    
    def record_recommendation_interaction(
        self, 
        user_id: str, 
        product_id: str, 
        interaction_type: str
    ) -> bool:
        """Record user interaction with recommendations (click, view, purchase, etc.)"""
        try:
            # This could be expanded to store interaction data in Neo4j
            # for improving future recommendations
            logger.info(f"Recorded {interaction_type} interaction for user {user_id} on product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Error recording recommendation interaction: {e}")
            return False


# Create service instance
recommendation_service = RecommendationService()