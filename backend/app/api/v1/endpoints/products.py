from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.product_service import product_service
from app.models.schemas import Product, ProductCreate, ProductCategory
from app.core.validation import ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    try:
        product = product_service.create_product(db, product_data.dict())
        return product
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of products to return"),
    category: Optional[ProductCategory] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    search: Optional[str] = Query(None, description="Search products by name or description"),
    db: Session = Depends(get_db)
):
    """Get products with optional filters"""
    try:
        if search:
            products = product_service.search_products(db, search, limit)
        elif category:
            products = product_service.get_products_by_category(db, category, limit)
        elif min_price is not None or max_price is not None:
            min_price = min_price or 0
            max_price = max_price or float('inf')
            products = product_service.get_products_by_price_range(db, min_price, max_price, limit)
        else:
            products = product_service.get_all_products(db, skip, limit)
        
        return products
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/featured", response_model=List[Product])
async def get_featured_products(
    limit: int = Query(20, ge=1, le=100, description="Number of featured products to return"),
    db: Session = Depends(get_db)
):
    """Get featured products"""
    try:
        products = product_service.get_featured_products(db, limit)
        return products
    except Exception as e:
        logger.error(f"Error getting featured products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/categories")
async def get_product_categories():
    """Get all available product categories"""
    return {
        "categories": [category.value for category in ProductCategory]
    }


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get product by ID"""
    try:
        product = product_service.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update product information"""
    try:
        product = product_service.update_product(db, product_id, update_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Delete a product"""
    try:
        success = product_service.delete_product(db, product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )