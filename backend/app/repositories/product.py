from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base import BaseRepository
from app.models.database import ProductModel
from app.models.schemas import ProductCreate, ProductCategory
import logging

logger = logging.getLogger(__name__)


class ProductRepository(BaseRepository[ProductModel]):
    """Repository for Product operations"""
    
    def __init__(self):
        super().__init__(ProductModel)
    
    def get_by_category(self, db: Session, category: ProductCategory, limit: int = 100) -> List[ProductModel]:
        """Get products by category"""
        try:
            return (
                db.query(ProductModel)
                .filter(ProductModel.category == category.value)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting products by category {category}: {e}")
            raise
    
    def search_products(self, db: Session, query: str, limit: int = 50) -> List[ProductModel]:
        """Search products by name or description"""
        try:
            return (
                db.query(ProductModel)
                .filter(
                    ProductModel.name.ilike(f"%{query}%") |
                    ProductModel.description.ilike(f"%{query}%")
                )
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error searching products with query '{query}': {e}")
            raise
    
    def get_by_price_range(self, db: Session, min_price: float, max_price: float, limit: int = 100) -> List[ProductModel]:
        """Get products within a price range"""
        try:
            return (
                db.query(ProductModel)
                .filter(
                    ProductModel.price >= min_price,
                    ProductModel.price <= max_price
                )
                .order_by(ProductModel.price.asc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting products by price range {min_price}-{max_price}: {e}")
            raise
    
    def create_product(self, db: Session, product: ProductCreate) -> ProductModel:
        """Create a new product"""
        product_data = {
            "name": product.name,
            "category": product.category.value,
            "price": product.price,
            "description": product.description,
            "image_url": product.image_url,
            "extra_data": product.metadata
        }
        return self.create(db, product_data)
    
    def get_featured_products(self, db: Session, limit: int = 20) -> List[ProductModel]:
        """Get featured products (sorted by creation date)"""
        try:
            return (
                db.query(ProductModel)
                .order_by(ProductModel.created_at.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting featured products: {e}")
            raise


# Create repository instance
product_repository = ProductRepository()