#!/usr/bin/env python3
"""
Seed script to populate the database with sample data for development and testing.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.database import Base, UserModel, ProductModel, PurchaseModel, UserInterestModel
from app.models.schemas import ProductCategory, InterestCategory
from app.services.knowledge_graph_service import knowledge_graph_service
import random
from datetime import datetime, timedelta
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_users() -> list:
    """Create sample users"""
    users = [
        {
            "email": "alice.johnson@email.com",
            "profile_data": {
                "name": "Alice Johnson",
                "age": 28,
                "location": "San Francisco, CA",
                "preferences": ["sustainable", "tech", "fitness"]
            }
        },
        {
            "email": "bob.smith@email.com", 
            "profile_data": {
                "name": "Bob Smith",
                "age": 34,
                "location": "New York, NY",
                "preferences": ["luxury", "fashion", "travel"]
            }
        },
        {
            "email": "carol.davis@email.com",
            "profile_data": {
                "name": "Carol Davis",
                "age": 42,
                "location": "Austin, TX",
                "preferences": ["home", "books", "cooking"]
            }
        },
        {
            "email": "david.wilson@email.com",
            "profile_data": {
                "name": "David Wilson",
                "age": 31,
                "location": "Seattle, WA",
                "preferences": ["gaming", "technology", "music"]
            }
        },
        {
            "email": "emma.brown@email.com",
            "profile_data": {
                "name": "Emma Brown",
                "age": 26,
                "location": "Los Angeles, CA",
                "preferences": ["beauty", "fashion", "fitness"]
            }
        }
    ]
    return users


def create_sample_products() -> list:
    """Create sample products across different categories"""
    products = [
        # Technology
        {
            "name": "Wireless Bluetooth Headphones",
            "category": ProductCategory.ELECTRONICS.value,
            "price": 199.99,
            "description": "Premium wireless headphones with noise cancellation and 30-hour battery life.",
            "image_url": "https://example.com/images/headphones.jpg",
            "extra_data": {"brand": "TechSound", "wireless": True, "battery_life": "30h"}
        },
        {
            "name": "Smart Fitness Watch",
            "category": ProductCategory.ELECTRONICS.value,
            "price": 299.99,
            "description": "Advanced fitness tracking with heart rate monitor, GPS, and sleep tracking.",
            "image_url": "https://example.com/images/smartwatch.jpg",
            "extra_data": {"brand": "FitTech", "features": ["GPS", "heart_rate", "sleep_tracking"]}
        },
        {
            "name": "4K Webcam",
            "category": ProductCategory.ELECTRONICS.value,
            "price": 149.99,
            "description": "Ultra HD webcam perfect for streaming and video calls.",
            "image_url": "https://example.com/images/webcam.jpg",
            "extra_data": {"resolution": "4K", "fps": 60}
        },
        
        # Fashion
        {
            "name": "Sustainable Cotton T-Shirt",
            "category": ProductCategory.CLOTHING.value,
            "price": 34.99,
            "description": "Eco-friendly organic cotton t-shirt in various colors.",
            "image_url": "https://example.com/images/tshirt.jpg",
            "extra_data": {"material": "organic_cotton", "sustainable": True, "sizes": ["S", "M", "L", "XL"]}
        },
        {
            "name": "Premium Denim Jeans",
            "category": ProductCategory.CLOTHING.value,
            "price": 89.99,
            "description": "High-quality denim jeans with perfect fit and durability.",
            "image_url": "https://example.com/images/jeans.jpg",
            "extra_data": {"material": "denim", "fit": "slim", "care": "machine_wash"}
        },
        {
            "name": "Cashmere Sweater",
            "category": ProductCategory.CLOTHING.value,
            "price": 179.99,
            "description": "Luxurious cashmere sweater for ultimate comfort and style.",
            "image_url": "https://example.com/images/sweater.jpg",
            "extra_data": {"material": "cashmere", "luxury": True, "season": "winter"}
        },
        
        # Home & Garden
        {
            "name": "Smart LED Light Bulbs (4-pack)",
            "category": ProductCategory.HOME_GARDEN.value,
            "price": 49.99,
            "description": "WiFi-enabled smart bulbs with color changing and dimming features.",
            "image_url": "https://example.com/images/smartbulbs.jpg",
            "extra_data": {"smart_home": True, "colors": "16_million", "app_controlled": True}
        },
        {
            "name": "Bamboo Kitchen Utensil Set",
            "category": ProductCategory.HOME_GARDEN.value,
            "price": 29.99,
            "description": "Eco-friendly bamboo kitchen utensils set with holder.",
            "image_url": "https://example.com/images/utensils.jpg",
            "extra_data": {"material": "bamboo", "eco_friendly": True, "pieces": 6}
        },
        {
            "name": "Memory Foam Pillow",
            "category": ProductCategory.HOME_GARDEN.value,
            "price": 59.99,
            "description": "Contoured memory foam pillow for better sleep and neck support.",
            "image_url": "https://example.com/images/pillow.jpg",
            "extra_data": {"material": "memory_foam", "sleep": True, "support": "neck"}
        },
        
        # Books & Media
        {
            "name": "The Art of Productivity",
            "category": ProductCategory.BOOKS_MEDIA.value,
            "price": 24.99,
            "description": "A comprehensive guide to mastering productivity and time management.",
            "image_url": "https://example.com/images/productivity_book.jpg",
            "extra_data": {"author": "Jane Expert", "pages": 320, "genre": "self_help"}
        },
        {
            "name": "Wireless Charging Pad",
            "category": ProductCategory.ELECTRONICS.value,
            "price": 39.99,
            "description": "Fast wireless charging pad compatible with all Qi-enabled devices.",
            "image_url": "https://example.com/images/charging_pad.jpg",
            "extra_data": {"wireless": True, "fast_charging": True, "compatibility": "Qi"}
        },
        
        # Beauty & Personal Care
        {
            "name": "Vitamin C Serum",
            "category": ProductCategory.BEAUTY_PERSONAL_CARE.value,
            "price": 45.99,
            "description": "Brightening vitamin C serum for radiant and healthy skin.",
            "image_url": "https://example.com/images/vitamin_c_serum.jpg",
            "extra_data": {"skincare": True, "vitamin_c": True, "volume": "30ml"}
        },
        {
            "name": "Natural Face Moisturizer",
            "category": ProductCategory.BEAUTY_PERSONAL_CARE.value,
            "price": 32.99,
            "description": "Hydrating face moisturizer with natural ingredients for all skin types.",
            "image_url": "https://example.com/images/moisturizer.jpg",
            "extra_data": {"natural": True, "skin_type": "all", "hydrating": True}
        },
        
        # Fitness Equipment
        {
            "name": "Yoga Mat Premium",
            "category": ProductCategory.FITNESS_EQUIPMENT.value,
            "price": 79.99,
            "description": "Extra thick premium yoga mat with superior grip and cushioning.",
            "image_url": "https://example.com/images/yoga_mat.jpg",
            "extra_data": {"thickness": "6mm", "material": "TPE", "eco_friendly": True}
        },
        {
            "name": "Resistance Bands Set",
            "category": ProductCategory.FITNESS_EQUIPMENT.value,
            "price": 24.99,
            "description": "Complete resistance bands set for full-body workouts.",
            "image_url": "https://example.com/images/resistance_bands.jpg",
            "extra_data": {"pieces": 5, "resistance_levels": ["light", "medium", "heavy"], "portable": True}
        }
    ]
    return products


def create_sample_interests() -> list:
    """Create sample user interests"""
    interests = [
        # Alice's interests (tech-savvy fitness enthusiast)
        {"category": InterestCategory.TECHNOLOGY, "value": "smart_home_devices", "confidence": 0.9, "source": "purchase"},
        {"category": InterestCategory.FITNESS, "value": "yoga", "confidence": 0.8, "source": "survey"},
        {"category": InterestCategory.FITNESS, "value": "running", "confidence": 0.7, "source": "behavior"},
        
        # Bob's interests (fashion and travel)
        {"category": InterestCategory.FASHION, "value": "luxury_brands", "confidence": 0.9, "source": "purchase"},
        {"category": InterestCategory.TRAVEL, "value": "international_destinations", "confidence": 0.8, "source": "survey"},
        {"category": InterestCategory.FASHION, "value": "designer_clothing", "confidence": 0.85, "source": "behavior"},
        
        # Carol's interests (home and books)
        {"category": InterestCategory.HOME, "value": "kitchen_gadgets", "confidence": 0.8, "source": "purchase"},
        {"category": InterestCategory.BOOKS, "value": "self_improvement", "confidence": 0.9, "source": "purchase"},
        {"category": InterestCategory.FOOD, "value": "healthy_cooking", "confidence": 0.7, "source": "behavior"},
        
        # David's interests (technology and music)
        {"category": InterestCategory.TECHNOLOGY, "value": "gaming_equipment", "confidence": 0.95, "source": "purchase"},
        {"category": InterestCategory.MUSIC, "value": "audio_equipment", "confidence": 0.8, "source": "purchase"},
        {"category": InterestCategory.TECHNOLOGY, "value": "programming", "confidence": 0.7, "source": "survey"},
        
        # Emma's interests (beauty and fashion)
        {"category": InterestCategory.BEAUTY, "value": "skincare_products", "confidence": 0.9, "source": "purchase"},
        {"category": InterestCategory.FASHION, "value": "trendy_clothing", "confidence": 0.8, "source": "behavior"},
        {"category": InterestCategory.FITNESS, "value": "pilates", "confidence": 0.6, "source": "survey"}
    ]
    return interests


def seed_database():
    """Main function to seed the database with sample data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        logger.info("Starting database seeding...")
        
        # Clear existing data
        logger.info("Clearing existing data...")
        db.query(PurchaseModel).delete()
        db.query(UserInterestModel).delete()
        db.query(ProductModel).delete()
        db.query(UserModel).delete()
        db.commit()
        
        # Create users
        logger.info("Creating sample users...")
        user_data = create_sample_users()
        users = []
        for user_info in user_data:
            user = UserModel(
                id=str(uuid.uuid4()),
                email=user_info["email"],
                profile_data=user_info["profile_data"]
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        logger.info(f"Created {len(users)} users")
        
        # Create products
        logger.info("Creating sample products...")
        product_data = create_sample_products()
        products = []
        for product_info in product_data:
            product = ProductModel(
                id=str(uuid.uuid4()),
                name=product_info["name"],
                category=product_info["category"],
                price=product_info["price"],
                description=product_info["description"],
                image_url=product_info["image_url"],
                extra_data=product_info["extra_data"]
            )
            db.add(product)
            products.append(product)
        
        db.commit()
        logger.info(f"Created {len(products)} products")
        
        # Create user interests
        logger.info("Creating sample user interests...")
        interest_data = create_sample_interests()
        interests = []
        for i, interest_info in enumerate(interest_data):
            user_index = i % len(users)  # Distribute interests among users
            interest = UserInterestModel(
                id=str(uuid.uuid4()),
                user_id=users[user_index].id,
                interest_category=interest_info["category"].value,
                interest_value=interest_info["value"],
                confidence_score=interest_info["confidence"],
                source=interest_info["source"]
            )
            db.add(interest)
            interests.append(interest)
        
        db.commit()
        logger.info(f"Created {len(interests)} user interests")
        
        # Create sample purchases
        logger.info("Creating sample purchases...")
        purchases = []
        for user in users:
            # Each user makes 2-5 purchases
            num_purchases = random.randint(2, 5)
            user_products = random.sample(products, num_purchases)
            
            for product in user_products:
                # Purchase within the last 90 days
                days_ago = random.randint(1, 90)
                purchase_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Add some variation to the price (discounts, etc.)
                price_variation = random.uniform(0.8, 1.0)
                final_price = product.price * price_variation
                
                purchase = PurchaseModel(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    product_id=product.id,
                    amount=round(final_price, 2),
                    quantity=random.randint(1, 3),
                    timestamp=purchase_date,
                    extra_data={"discount_applied": price_variation < 0.95}
                )
                db.add(purchase)
                purchases.append(purchase)
        
        db.commit()
        logger.info(f"Created {len(purchases)} purchases")
        
        # Add data to knowledge graph if available
        logger.info("Adding data to knowledge graph...")
        try:
            for user in users:
                from app.models.schemas import User
                user_obj = User(
                    id=user.id,
                    email=user.email,
                    profile_data=user.profile_data,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                knowledge_graph_service.create_user_node(user_obj)
            
            for product in products:
                from app.models.schemas import Product, ProductCategory
                product_obj = Product(
                    id=product.id,
                    name=product.name,
                    category=ProductCategory(product.category),
                    price=product.price,
                    description=product.description,
                    image_url=product.image_url,
                    metadata=product.extra_data,
                    created_at=product.created_at
                )
                knowledge_graph_service.create_product_node(product_obj)
            
            for purchase in purchases:
                from app.models.schemas import Purchase
                purchase_obj = Purchase(
                    id=purchase.id,
                    user_id=purchase.user_id,
                    product_id=purchase.product_id,
                    amount=purchase.amount,
                    quantity=purchase.quantity,
                    metadata=purchase.extra_data,
                    timestamp=purchase.timestamp
                )
                knowledge_graph_service.create_purchase_relationship(purchase_obj)
            
            for interest in interests:
                from app.models.schemas import UserInterest, InterestCategory
                interest_obj = UserInterest(
                    id=interest.id,
                    user_id=interest.user_id,
                    interest_category=InterestCategory(interest.interest_category),
                    interest_value=interest.interest_value,
                    confidence_score=interest.confidence_score,
                    source=interest.source,
                    created_at=interest.created_at
                )
                knowledge_graph_service.create_interest_relationship(interest_obj)
            
            logger.info("Successfully added data to knowledge graph")
        except Exception as e:
            logger.warning(f"Could not add data to knowledge graph: {e}")
        
        logger.info("Database seeding completed successfully!")
        logger.info(f"Summary:")
        logger.info(f"  - Users: {len(users)}")
        logger.info(f"  - Products: {len(products)}")
        logger.info(f"  - Interests: {len(interests)}")
        logger.info(f"  - Purchases: {len(purchases)}")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()