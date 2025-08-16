from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.user_interest import user_interest_repository
from app.repositories.purchase import purchase_repository
from app.services.knowledge_graph_service import knowledge_graph_service
from app.models.schemas import (
    UserInterest, UserInterestCreate, InterestCategory, 
    Purchase, ProductCategory
)
from app.core.validation import validate_interest_data, ValidationError
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class UserInterestService:
    """Service for managing user interests and analysis"""
    
    def __init__(self):
        self.interest_repo = user_interest_repository
        self.purchase_repo = purchase_repository
        self.kg_service = knowledge_graph_service
    
    def add_user_interest(self, db: Session, interest_data: Dict[str, Any]) -> UserInterest:
        """Add a new user interest with validation"""
        try:
            validated_interest = validate_interest_data(interest_data)
            
            # Check for duplicate interests and update if exists
            existing_interest = self.interest_repo.find_duplicate_interest(
                db, 
                validated_interest.user_id,
                validated_interest.interest_category.value,
                validated_interest.interest_value
            )
            
            if existing_interest:
                # Update confidence score (take higher score)
                new_score = max(existing_interest.confidence_score, validated_interest.confidence_score)
                updated_interest = self.interest_repo.update_confidence_score(
                    db, existing_interest.id, new_score
                )
                if updated_interest:
                    logger.info(f"Updated existing interest for user {validated_interest.user_id}")
                    return UserInterest.model_validate(updated_interest)
            
            # Create new interest
            db_interest = self.interest_repo.create_interest(db, validated_interest)
            
            # Add to knowledge graph
            interest_obj = UserInterest.model_validate(db_interest)
            self.kg_service.create_interest_relationship(interest_obj)
            
            logger.info(f"Added new interest for user {validated_interest.user_id}")
            return interest_obj
        
        except Exception as e:
            logger.error(f"Error adding user interest: {e}")
            raise
    
    def get_user_interests(self, db: Session, user_id: str, limit: int = 100) -> List[UserInterest]:
        """Get all interests for a user"""
        try:
            db_interests = self.interest_repo.get_by_user_id(db, user_id, limit)
            return [UserInterest.model_validate(interest) for interest in db_interests]
        except Exception as e:
            logger.error(f"Error getting interests for user {user_id}: {e}")
            raise
    
    def get_interests_by_category(self, db: Session, user_id: str, category: InterestCategory) -> List[UserInterest]:
        """Get user interests by category"""
        try:
            db_interests = self.interest_repo.get_by_category(db, user_id, category)
            return [UserInterest.model_validate(interest) for interest in db_interests]
        except Exception as e:
            logger.error(f"Error getting interests by category for user {user_id}: {e}")
            raise
    
    def analyze_purchase_interests(self, db: Session, user_id: str) -> List[UserInterest]:
        """Analyze user's purchase history to infer interests"""
        try:
            purchases = self.purchase_repo.get_by_user_id(db, user_id, 100)
            if not purchases:
                return []
            
            # Analyze purchase patterns
            category_counts = Counter()
            total_spent_by_category = {}
            
            for purchase in purchases:
                # This would need product information to determine category
                # For now, we'll create a placeholder implementation
                category_counts['unknown'] += 1
                total_spent_by_category['unknown'] = total_spent_by_category.get('unknown', 0) + purchase.amount
            
            # Generate interest entries based on purchase patterns
            generated_interests = []
            for category, count in category_counts.most_common(5):
                if count >= 2:  # Only if user has multiple purchases in category
                    try:
                        # Map purchase categories to interest categories
                        interest_category = self._map_purchase_to_interest_category(category)
                        if interest_category:
                            confidence_score = min(count * 0.1, 1.0)  # Simple confidence calculation
                            
                            interest_data = {
                                "user_id": user_id,
                                "interest_category": interest_category,
                                "interest_value": f"frequent_buyer_{category}",
                                "confidence_score": confidence_score,
                                "source": "purchase_analysis"
                            }
                            
                            interest = self.add_user_interest(db, interest_data)
                            generated_interests.append(interest)
                    except Exception as e:
                        logger.warning(f"Error creating interest from purchase analysis: {e}")
                        continue
            
            logger.info(f"Generated {len(generated_interests)} interests from purchase analysis for user {user_id}")
            return generated_interests
        
        except Exception as e:
            logger.error(f"Error analyzing purchase interests for user {user_id}: {e}")
            return []
    
    def get_interest_summary(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get comprehensive interest summary for a user"""
        try:
            # Get all interests
            interests = self.get_user_interests(db, user_id)
            
            # Get top categories
            top_categories = self.interest_repo.get_top_interests_by_category(db, user_id, 10)
            
            # Calculate overall interest scores
            category_scores = {}
            for interest in interests:
                category = interest.interest_category.value
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(interest.confidence_score)
            
            # Average scores by category
            avg_category_scores = {
                category: sum(scores) / len(scores)
                for category, scores in category_scores.items()
            }
            
            return {
                "user_id": user_id,
                "total_interests": len(interests),
                "top_categories": top_categories,
                "average_category_scores": avg_category_scores,
                "highest_confidence_interests": [
                    {
                        "category": interest.interest_category.value,
                        "value": interest.interest_value,
                        "confidence": interest.confidence_score,
                        "source": interest.source
                    }
                    for interest in sorted(interests, key=lambda x: x.confidence_score, reverse=True)[:5]
                ],
                "recent_interests": [
                    {
                        "category": interest.interest_category.value,
                        "value": interest.interest_value,
                        "confidence": interest.confidence_score,
                        "source": interest.source
                    }
                    for interest in sorted(interests, key=lambda x: x.created_at, reverse=True)[:5]
                ]
            }
        
        except Exception as e:
            logger.error(f"Error getting interest summary for user {user_id}: {e}")
            raise
    
    def update_interest_confidence(self, db: Session, interest_id: str, new_score: float) -> Optional[UserInterest]:
        """Update confidence score for an interest"""
        try:
            db_interest = self.interest_repo.update_confidence_score(db, interest_id, new_score)
            if db_interest:
                logger.info(f"Updated confidence score for interest {interest_id} to {new_score}")
                return UserInterest.model_validate(db_interest)
            return None
        except Exception as e:
            logger.error(f"Error updating interest confidence for {interest_id}: {e}")
            raise
    
    def delete_user_interest(self, db: Session, interest_id: str) -> bool:
        """Delete a user interest"""
        try:
            success = self.interest_repo.delete(db, interest_id)
            if success:
                logger.info(f"Deleted interest {interest_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting interest {interest_id}: {e}")
            raise
    
    def _map_purchase_to_interest_category(self, purchase_category: str) -> Optional[InterestCategory]:
        """Map purchase category to interest category"""
        mapping = {
            "clothing": InterestCategory.FASHION,
            "electronics": InterestCategory.TECHNOLOGY,
            "food_beverage": InterestCategory.FOOD,
            "travel_services": InterestCategory.TRAVEL,
            "fitness_equipment": InterestCategory.FITNESS,
            "home_garden": InterestCategory.HOME,
            "beauty_personal_care": InterestCategory.BEAUTY,
            "books_media": InterestCategory.BOOKS,
            "sports_outdoors": InterestCategory.SPORTS
        }
        return mapping.get(purchase_category)


# Create service instance
user_interest_service = UserInterestService()