#!/usr/bin/env python3
"""Test database connection and basic operations"""

from app.core.database import check_db_connection, create_tables
from app.repositories.user import user_repository
from app.repositories.purchase import purchase_repository
from app.models.schemas import UserCreate, PurchaseCreate
from app.core.database import SessionLocal

def test_connection():
    print("Testing database connection...")
    
    # Test connection
    if check_db_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return
    
    # Test basic operations
    db = SessionLocal()
    try:
        # Create a test user
        user_data = UserCreate(
            email="test@hackathon.com",
            profile_data={"age": 25, "interests": ["tech", "ai"]}
        )
        user = user_repository.create_user(db, user_data)
        print(f"✅ Created user: {user.email} (ID: {user.id})")
        
        # Create a test purchase
        purchase_data = PurchaseCreate(
            user_id=user.id,
            product_id="laptop-123",
            amount=999.99,
            quantity=1
        )
        purchase = purchase_repository.create_purchase(db, purchase_data)
        print(f"✅ Created purchase: ${purchase.amount} for user {user.email}")
        
        # Get user purchases
        purchases = purchase_repository.get_by_user_id(db, user.id)
        print(f"✅ Found {len(purchases)} purchases for user")
        
        # Get total spent
        total = purchase_repository.get_user_total_spent(db, user.id)
        print(f"✅ Total spent by user: ${total}")
        
        print("\n🎉 All database operations working correctly!")
        
    except Exception as e:
        print(f"❌ Error during database operations: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()