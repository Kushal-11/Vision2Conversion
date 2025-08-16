from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    profile_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProductModel(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, default="")
    image_url = Column(String(500))
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PurchaseModel(Base):
    __tablename__ = "purchases"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    extra_data = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class UserInterestModel(Base):
    __tablename__ = "user_interests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    interest_category = Column(String(50), nullable=False)
    interest_value = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())