from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.recommendation_service import recommendation_service
from app.services.user_data_service import user_data_service
from app.services.user_interest_service import user_interest_service
from app.services.product_service import product_service
from app.models.schemas import (
    VisionBoardRequest, VisionBoard, Product, ProductCategory, User
)
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class VisionBoardService:
    """Service for generating personalized vision boards"""
    
    def __init__(self):
        self.recommendation_service = recommendation_service
        self.user_service = user_data_service
        self.interest_service = user_interest_service
        self.product_service = product_service
    
    def generate_vision_board(self, db: Session, request: VisionBoardRequest) -> VisionBoard:
        """Generate a personalized vision board for a user"""
        try:
            # Get user information
            user = self.user_service.get_user_by_id(db, request.user_id)
            if not user:
                raise ValueError(f"User {request.user_id} not found")
            
            # Get user interests to determine theme if not provided
            interests = self.interest_service.get_user_interests(db, request.user_id, 10)
            
            # Determine theme and products
            if request.theme:
                theme = request.theme
            else:
                theme = self._determine_theme_from_interests(interests)
            
            # Get products for vision board
            products = self._select_vision_board_products(
                db, request.user_id, request.categories, request.product_limit
            )
            
            if len(products) < 4:
                # Fallback to featured products if not enough personalized ones
                featured = self.product_service.get_featured_products(db, request.product_limit)
                products.extend(featured[:request.product_limit - len(products)])
            
            # Generate title and description
            title, description = self._generate_vision_board_content(user, theme, interests, products)
            
            # Create layout configuration
            layout_data = self._create_layout_configuration(products, request.product_limit)
            
            # Create style configuration
            style_config = self._create_style_configuration(request.style, theme)
            
            vision_board = VisionBoard(
                user_id=request.user_id,
                title=title,
                description=description,
                products=products[:request.product_limit],
                layout_data=layout_data,
                style_config=style_config
            )
            
            logger.info(f"Generated vision board '{title}' for user {request.user_id}")
            return vision_board
        
        except Exception as e:
            logger.error(f"Error generating vision board: {e}")
            raise
    
    def _determine_theme_from_interests(self, interests: List[Any]) -> str:
        """Determine vision board theme based on user interests"""
        if not interests:
            return "Lifestyle Inspiration"
        
        # Count interest categories
        category_counts = {}
        for interest in interests:
            category = interest.interest_category.value
            category_counts[category] = category_counts.get(category, 0) + interest.confidence_score
        
        # Get dominant category
        dominant_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "lifestyle"
        
        theme_mapping = {
            "fashion": "Style & Fashion Goals",
            "technology": "Tech-Savvy Lifestyle",
            "food": "Culinary Adventures", 
            "travel": "Wanderlust Dreams",
            "fitness": "Health & Wellness Journey",
            "home": "Dream Home Inspiration",
            "beauty": "Beauty & Self-Care",
            "books": "Literary Lifestyle",
            "music": "Creative Expression",
            "sports": "Active Lifestyle Goals"
        }
        
        return theme_mapping.get(dominant_category, "Personalized Lifestyle")
    
    def _select_vision_board_products(
        self, 
        db: Session, 
        user_id: str, 
        categories: List[ProductCategory], 
        limit: int
    ) -> List[Product]:
        """Select products for vision board based on user preferences"""
        products = []
        
        # If specific categories requested, get products from those
        if categories:
            for category in categories:
                category_products = self.product_service.get_products_by_category(db, category, limit // len(categories) + 2)
                products.extend(category_products)
        else:
            # Get personalized recommendations
            recommendations = self.recommendation_service.get_personalized_recommendations(db, user_id, limit * 2)
            
            # Get product details
            for rec in recommendations:
                product = self.product_service.get_product_by_id(db, rec.product_id)
                if product:
                    products.append(product)
        
        # Ensure diversity in product selection
        products = self._ensure_product_diversity(products, limit)
        
        # Shuffle for visual variety
        random.shuffle(products)
        
        return products[:limit]
    
    def _ensure_product_diversity(self, products: List[Product], limit: int) -> List[Product]:
        """Ensure diversity in product categories and price ranges"""
        if len(products) <= limit:
            return products
        
        # Group by category
        category_groups = {}
        for product in products:
            category = product.category.value
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(product)
        
        # Select diverse products
        diverse_products = []
        categories = list(category_groups.keys())
        
        while len(diverse_products) < limit and categories:
            for category in categories[:]:
                if category_groups[category]:
                    diverse_products.append(category_groups[category].pop(0))
                    if len(diverse_products) >= limit:
                        break
                else:
                    categories.remove(category)
        
        return diverse_products
    
    def _generate_vision_board_content(
        self, 
        user: User, 
        theme: str, 
        interests: List[Any], 
        products: List[Product]
    ) -> tuple[str, str]:
        """Generate title and description for vision board"""
        user_name = user.profile_data.get("name", user.email.split("@")[0].title())
        
        # Generate personalized title
        title = f"{user_name}'s {theme}"
        
        # Generate description
        if interests:
            top_categories = list(set([i.interest_category.value.replace("_", " ").title() for i in interests[:3]]))
            description = f"A curated collection reflecting your interests in {', '.join(top_categories)}. "
        else:
            description = "A personalized collection of inspiring products. "
        
        description += f"Featuring {len(products)} carefully selected items to inspire your lifestyle goals."
        
        return title, description
    
    def _create_layout_configuration(self, products: List[Product], grid_size: int) -> Dict[str, Any]:
        """Create layout configuration for vision board"""
        # Determine grid dimensions
        if grid_size <= 4:
            rows, cols = 2, 2
        elif grid_size <= 6:
            rows, cols = 2, 3
        elif grid_size <= 9:
            rows, cols = 3, 3
        elif grid_size <= 12:
            rows, cols = 3, 4
        else:
            rows, cols = 4, 4
        
        # Create grid positions
        positions = []
        for i in range(min(grid_size, len(products))):
            row = i // cols
            col = i % cols
            positions.append({
                "product_id": products[i].id,
                "row": row,
                "col": col,
                "width": 1,
                "height": 1
            })
        
        return {
            "grid_rows": rows,
            "grid_cols": cols,
            "positions": positions,
            "spacing": "medium",
            "border_radius": "8px"
        }
    
    def _create_style_configuration(self, style: str, theme: str) -> Dict[str, Any]:
        """Create style configuration for vision board"""
        style_configs = {
            "modern": {
                "background_color": "#ffffff",
                "border_color": "#e1e8ed",
                "text_color": "#14171a",
                "accent_color": "#1da1f2",
                "font_family": "Arial, sans-serif",
                "border_width": "1px",
                "shadow": "0 2px 8px rgba(0,0,0,0.1)"
            },
            "minimal": {
                "background_color": "#fafafa",
                "border_color": "#f0f0f0",
                "text_color": "#333333",
                "accent_color": "#000000",
                "font_family": "Helvetica, sans-serif",
                "border_width": "0px",
                "shadow": "none"
            },
            "colorful": {
                "background_color": "#ffffff",
                "border_color": "#ff6b6b",
                "text_color": "#2d3436",
                "accent_color": "#fd79a8",
                "font_family": "Arial, sans-serif",
                "border_width": "2px",
                "shadow": "0 4px 12px rgba(0,0,0,0.15)"
            },
            "elegant": {
                "background_color": "#f8f9fa",
                "border_color": "#6c757d",
                "text_color": "#212529",
                "accent_color": "#495057",
                "font_family": "Georgia, serif",
                "border_width": "1px",
                "shadow": "0 2px 6px rgba(0,0,0,0.08)"
            }
        }
        
        config = style_configs.get(style, style_configs["modern"])
        config["theme"] = theme
        config["style_name"] = style
        
        return config
    
    def get_vision_board_themes(self) -> List[str]:
        """Get available vision board themes"""
        return [
            "Style & Fashion Goals",
            "Tech-Savvy Lifestyle", 
            "Culinary Adventures",
            "Wanderlust Dreams",
            "Health & Wellness Journey",
            "Dream Home Inspiration",
            "Beauty & Self-Care",
            "Literary Lifestyle",
            "Creative Expression",
            "Active Lifestyle Goals",
            "Minimalist Living",
            "Luxury Lifestyle",
            "Eco-Friendly Living",
            "Professional Success",
            "Family & Relationships"
        ]
    
    def get_style_options(self) -> List[Dict[str, str]]:
        """Get available style options for vision boards"""
        return [
            {"name": "modern", "description": "Clean and contemporary design"},
            {"name": "minimal", "description": "Simple and uncluttered layout"},
            {"name": "colorful", "description": "Vibrant and energetic styling"},
            {"name": "elegant", "description": "Sophisticated and refined appearance"}
        ]


# Create service instance
vision_board_service = VisionBoardService()