import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.models.database import UserModel, PurchaseModel
from app.repositories.user import user_repository
from app.repositories.purchase import purchase_repository
from app.models.schemas import UserCreate, PurchaseCreate


# Test database URL (using same as main for now)
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5433/marketing_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


class TestUserRepository:
    def test_create_user(self, db_session):
        user_data = UserCreate(
            email="test@example.com",
            profile_data={"age": 25, "location": "NYC"}
        )
        
        user = user_repository.create_user(db_session, user_data)
        
        assert user.email == "test@example.com"
        assert user.profile_data["age"] == 25
        assert user.id is not None
    
    def test_get_user_by_email(self, db_session):
        # Create a user first
        user_data = UserCreate(email="test2@example.com")
        created_user = user_repository.create_user(db_session, user_data)
        
        # Get user by email
        found_user = user_repository.get_by_email(db_session, "test2@example.com")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test2@example.com"
    
    def test_get_user_by_id(self, db_session):
        # Create a user first
        user_data = UserCreate(email="test3@example.com")
        created_user = user_repository.create_user(db_session, user_data)
        
        # Get user by ID
        found_user = user_repository.get_by_id(db_session, created_user.id)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test3@example.com"
    
    def test_update_profile_data(self, db_session):
        # Create a user first
        user_data = UserCreate(
            email="test4@example.com",
            profile_data={"age": 25}
        )
        created_user = user_repository.create_user(db_session, user_data)
        
        # Update profile data
        new_profile_data = {"location": "SF", "age": 26}
        updated_user = user_repository.update_profile_data(
            db_session, created_user.id, new_profile_data
        )
        
        assert updated_user is not None
        assert updated_user.profile_data["age"] == 26
        assert updated_user.profile_data["location"] == "SF"


class TestPurchaseRepository:
    def test_create_purchase(self, db_session):
        # Create a user first
        user_data = UserCreate(email="buyer@example.com")
        user = user_repository.create_user(db_session, user_data)
        
        # Create a purchase
        purchase_data = PurchaseCreate(
            user_id=user.id,
            product_id="product123",
            amount=99.99,
            quantity=2
        )
        
        purchase = purchase_repository.create_purchase(db_session, purchase_data)
        
        assert purchase.user_id == user.id
        assert purchase.product_id == "product123"
        assert purchase.amount == 99.99
        assert purchase.quantity == 2
    
    def test_get_purchases_by_user_id(self, db_session):
        # Create a user first
        user_data = UserCreate(email="buyer2@example.com")
        user = user_repository.create_user(db_session, user_data)
        
        # Create multiple purchases
        for i in range(3):
            purchase_data = PurchaseCreate(
                user_id=user.id,
                product_id=f"product{i}",
                amount=10.0 * (i + 1)
            )
            purchase_repository.create_purchase(db_session, purchase_data)
        
        # Get purchases by user ID
        purchases = purchase_repository.get_by_user_id(db_session, user.id)
        
        assert len(purchases) == 3
        assert all(p.user_id == user.id for p in purchases)
    
    def test_get_user_total_spent(self, db_session):
        # Create a user first
        user_data = UserCreate(email="spender@example.com")
        user = user_repository.create_user(db_session, user_data)
        
        # Create purchases
        amounts = [25.50, 75.25, 100.00]
        for amount in amounts:
            purchase_data = PurchaseCreate(
                user_id=user.id,
                product_id="product123",
                amount=amount
            )
            purchase_repository.create_purchase(db_session, purchase_data)
        
        # Get total spent
        total = purchase_repository.get_user_total_spent(db_session, user.id)
        
        assert total == sum(amounts)