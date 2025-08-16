import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import ProductCategory

client = TestClient(app)


class TestProductAPI:
    
    def test_create_product(self):
        """Test creating a new product"""
        product_data = {
            "name": "Test Wireless Headphones",
            "category": ProductCategory.ELECTRONICS.value,
            "price": 199.99,
            "description": "High-quality wireless headphones for testing",
            "image_url": "https://example.com/headphones.jpg",
            "metadata": {"brand": "TestBrand", "wireless": True}
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Wireless Headphones"
        assert data["category"] == ProductCategory.ELECTRONICS.value
        assert data["price"] == 199.99
        assert "id" in data
        
        return data["id"]
    
    def test_get_products(self):
        """Test getting products with default parameters"""
        response = client.get("/api/v1/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_products_with_filters(self):
        """Test getting products with various filters"""
        # Test category filter
        response = client.get(f"/api/v1/products/?category={ProductCategory.ELECTRONICS.value}")
        assert response.status_code == 200
        
        # Test price range filter
        response = client.get("/api/v1/products/?min_price=100&max_price=300")
        assert response.status_code == 200
        
        # Test search filter
        response = client.get("/api/v1/products/?search=headphones")
        assert response.status_code == 200
        
        # Test pagination
        response = client.get("/api/v1/products/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_get_product_by_id(self):
        """Test getting a specific product by ID"""
        # Create a product first
        product_id = self.test_create_product()
        
        response = client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Test Wireless Headphones"
    
    def test_get_featured_products(self):
        """Test getting featured products"""
        response = client.get("/api/v1/products/featured")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 20  # Default limit
    
    def test_get_product_categories(self):
        """Test getting available product categories"""
        response = client.get("/api/v1/products/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert ProductCategory.ELECTRONICS.value in data["categories"]
    
    def test_update_product(self):
        """Test updating a product"""
        # Create a product first
        product_id = self.test_create_product()
        
        update_data = {
            "price": 179.99,
            "description": "Updated description with new features"
        }
        
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 179.99
        assert "Updated description" in data["description"]
    
    def test_delete_product(self):
        """Test deleting a product"""
        # Create a product first
        product_id = self.test_create_product()
        
        response = client.delete(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 204
        
        # Verify product is deleted
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 404
    
    def test_product_not_found(self):
        """Test getting non-existent product"""
        response = client.get("/api/v1/products/nonexistent-id")
        assert response.status_code == 404
    
    def test_invalid_product_data(self):
        """Test creating product with invalid data"""
        invalid_data = {
            "name": "",  # Empty name
            "category": "invalid_category",
            "price": -10  # Negative price
        }
        
        response = client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_multiple_products(self):
        """Test creating multiple products for search/filter testing"""
        products = [
            {
                "name": "Gaming Laptop",
                "category": ProductCategory.ELECTRONICS.value,
                "price": 1299.99,
                "description": "High-performance gaming laptop"
            },
            {
                "name": "Cotton T-Shirt",
                "category": ProductCategory.CLOTHING.value,
                "price": 29.99,
                "description": "Comfortable cotton t-shirt"
            },
            {
                "name": "Coffee Maker",
                "category": ProductCategory.HOME_GARDEN.value,
                "price": 89.99,
                "description": "Automatic drip coffee maker"
            }
        ]
        
        created_ids = []
        for product_data in products:
            response = client.post("/api/v1/products/", json=product_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        return created_ids