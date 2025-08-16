from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.product import product_repository
from app.models.schemas import Product, ProductCreate, ProductCategory
from app.core.validation import validate_product_data, ValidationError
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Service for managing product operations"""
    
    def __init__(self):
        self.product_repo = product_repository
    
    def create_product(self, db: Session, product_data: Dict[str, Any]) -> Product:
        """Create a new product with validation"""
        try:
            validated_product = validate_product_data(product_data)
            db_product = self.product_repo.create_product(db, validated_product)
            logger.info(f"Created product: {db_product.name}")
            return Product.model_validate(db_product)
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise
    
    def get_product_by_id(self, db: Session, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        try:
            db_product = self.product_repo.get_by_id(db, product_id)
            if not db_product:
                return None
            return Product.model_validate(db_product)
        except Exception as e:
            logger.error(f"Error getting product by ID {product_id}: {e}")
            raise
    
    def get_products_by_category(self, db: Session, category: ProductCategory, limit: int = 100) -> List[Product]:
        """Get products by category"""
        try:
            db_products = self.product_repo.get_by_category(db, category, limit)
            return [Product.model_validate(p) for p in db_products]
        except Exception as e:
            logger.error(f"Error getting products by category {category}: {e}")
            raise
    
    def search_products(self, db: Session, query: str, limit: int = 50) -> List[Product]:
        """Search products by name or description"""
        try:
            db_products = self.product_repo.search_products(db, query, limit)
            return [Product.model_validate(p) for p in db_products]
        except Exception as e:
            logger.error(f"Error searching products with query '{query}': {e}")
            raise
    
    def get_products_by_price_range(self, db: Session, min_price: float, max_price: float, limit: int = 100) -> List[Product]:
        """Get products within a price range"""
        try:
            db_products = self.product_repo.get_by_price_range(db, min_price, max_price, limit)
            return [Product.model_validate(p) for p in db_products]
        except Exception as e:
            logger.error(f"Error getting products by price range {min_price}-{max_price}: {e}")
            raise
    
    def get_featured_products(self, db: Session, limit: int = 20) -> List[Product]:
        """Get featured products"""
        try:
            db_products = self.product_repo.get_featured_products(db, limit)
            return [Product.model_validate(p) for p in db_products]
        except Exception as e:
            logger.error(f"Error getting featured products: {e}")
            raise
    
    def update_product(self, db: Session, product_id: str, update_data: Dict[str, Any]) -> Optional[Product]:
        """Update product information"""
        try:
            # Convert category enum to string if present
            if 'category' in update_data and hasattr(update_data['category'], 'value'):
                update_data['category'] = update_data['category'].value
            
            # Move metadata to extra_data for database storage
            if 'metadata' in update_data:
                update_data['extra_data'] = update_data.pop('metadata')
            
            db_product = self.product_repo.update(db, product_id, update_data)
            if not db_product:
                return None
            
            logger.info(f"Updated product: {product_id}")
            return Product.model_validate(db_product)
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise
    
    def delete_product(self, db: Session, product_id: str) -> bool:
        """Delete a product"""
        try:
            success = self.product_repo.delete(db, product_id)
            if success:
                logger.info(f"Deleted product: {product_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise
    
    def get_all_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        try:
            db_products = self.product_repo.get_multi(db, skip, limit)
            return [Product.model_validate(p) for p in db_products]
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            raise


# Create service instance
product_service = ProductService()