import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import EmailTemplateType, ProductCategory

client = TestClient(app)


class TestMarketingAPI:
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test user for marketing tests"""
        # Create test user
        user_data = {
            "email": "marketing_test@example.com",
            "profile_data": {"name": "Marketing Test User", "age": 28}
        }
        
        user_response = client.post("/api/v1/users/", json=user_data)
        assert user_response.status_code == 201
        self.user_id = user_response.json()["id"]
        
        # Create test products
        product_data = {
            "name": "Marketing Test Product",
            "category": ProductCategory.ELECTRONICS.value,
            "price": 199.99,
            "description": "A great product for testing marketing features"
        }
        
        product_response = client.post("/api/v1/products/", json=product_data)
        assert product_response.status_code == 201
        self.product_id = product_response.json()["id"]
        
        # Add some interests
        interest_data = {
            "interest_category": "technology",
            "interest_value": "smartphones",
            "confidence_score": 0.8,
            "source": "test"
        }
        
        interest_response = client.post(
            f"/api/v1/interests/users/{self.user_id}/interests", 
            json=interest_data
        )
        # Note: This might fail if the interests endpoint is not properly set up
        # but we continue with the marketing tests
    
    def test_generate_personalized_email(self):
        """Test generating personalized email content"""
        email_request = {
            "user_id": self.user_id,
            "template_type": EmailTemplateType.PERSONALIZED_RECOMMENDATIONS.value,
            "additional_data": {"campaign_name": "test_campaign"},
            "recommendations_limit": 3
        }
        
        response = client.post("/api/v1/marketing/emails/generate", json=email_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == self.user_id
        assert data["template_type"] == EmailTemplateType.PERSONALIZED_RECOMMENDATIONS.value
        assert "subject" in data
        assert "html_content" in data
        assert "text_content" in data
        assert isinstance(data["recommendations"], list)
    
    def test_generate_welcome_email(self):
        """Test generating welcome email"""
        email_request = {
            "user_id": self.user_id,
            "template_type": EmailTemplateType.WELCOME.value,
            "recommendations_limit": 5
        }
        
        response = client.post("/api/v1/marketing/emails/generate", json=email_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["template_type"] == EmailTemplateType.WELCOME.value
        assert "Welcome" in data["subject"] or "welcome" in data["subject"]
    
    def test_get_email_templates(self):
        """Test getting available email templates"""
        response = client.get("/api/v1/marketing/emails/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check that template has required fields
        template = data[0]
        assert "id" in template
        assert "name" in template
        assert "template_type" in template
        assert "subject_template" in template
        assert "html_template" in template
        assert "text_template" in template
    
    def test_preview_email_template(self):
        """Test previewing email template"""
        template_type = EmailTemplateType.PERSONALIZED_RECOMMENDATIONS.value
        response = client.get(f"/api/v1/marketing/emails/templates/{template_type}/preview")
        
        assert response.status_code == 200
        data = response.json()
        assert "subject" in data
        assert "html_content" in data
        assert "text_content" in data
    
    def test_get_email_template_types(self):
        """Test getting available email template types"""
        response = client.get("/api/v1/marketing/emails/template-types")
        
        assert response.status_code == 200
        data = response.json()
        assert "template_types" in data
        assert isinstance(data["template_types"], list)
        assert EmailTemplateType.PERSONALIZED_RECOMMENDATIONS.value in data["template_types"]
        assert EmailTemplateType.WELCOME.value in data["template_types"]
    
    def test_generate_vision_board(self):
        """Test generating vision board"""
        vision_board_request = {
            "user_id": self.user_id,
            "theme": "Tech Enthusiast",
            "categories": [ProductCategory.ELECTRONICS.value],
            "product_limit": 6,
            "style": "modern"
        }
        
        response = client.post("/api/v1/marketing/vision-boards/generate", json=vision_board_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == self.user_id
        assert "title" in data
        assert "description" in data
        assert "products" in data
        assert "layout_data" in data
        assert "style_config" in data
        assert len(data["products"]) <= 6
    
    def test_generate_vision_board_without_theme(self):
        """Test generating vision board without specified theme"""
        vision_board_request = {
            "user_id": self.user_id,
            "product_limit": 4,
            "style": "minimal"
        }
        
        response = client.post("/api/v1/marketing/vision-boards/generate", json=vision_board_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert len(data["products"]) <= 4
        assert data["style_config"]["style_name"] == "minimal"
    
    def test_get_vision_board_themes(self):
        """Test getting available vision board themes"""
        response = client.get("/api/v1/marketing/vision-boards/themes")
        
        assert response.status_code == 200
        data = response.json()
        assert "themes" in data
        assert isinstance(data["themes"], list)
        assert len(data["themes"]) > 0
    
    def test_get_vision_board_styles(self):
        """Test getting available vision board styles"""
        response = client.get("/api/v1/marketing/vision-boards/styles")
        
        assert response.status_code == 200
        data = response.json()
        assert "styles" in data
        assert isinstance(data["styles"], list)
        
        # Check style structure
        style = data["styles"][0]
        assert "name" in style
        assert "description" in style
    
    def test_create_email_campaign(self):
        """Test creating email campaign for multiple users"""
        # Create another test user
        user_data2 = {
            "email": "campaign_test2@example.com",
            "profile_data": {"name": "Campaign User 2"}
        }
        user_response2 = client.post("/api/v1/users/", json=user_data2)
        assert user_response2.status_code == 201
        user_id2 = user_response2.json()["id"]
        
        campaign_data = {
            "user_ids": [self.user_id, user_id2],
            "template_type": EmailTemplateType.WELCOME.value,
            "additional_data": {"campaign_id": "test_campaign_123"}
        }
        
        response = client.post("/api/v1/marketing/campaigns/email", json=campaign_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["total_users"] == 2
        assert "successful" in data
        assert "failed" in data
        assert "results" in data
    
    def test_email_generation_user_not_found(self):
        """Test email generation for non-existent user"""
        email_request = {
            "user_id": "nonexistent-user-id",
            "template_type": EmailTemplateType.WELCOME.value
        }
        
        response = client.post("/api/v1/marketing/emails/generate", json=email_request)
        assert response.status_code == 404
    
    def test_vision_board_user_not_found(self):
        """Test vision board generation for non-existent user"""
        vision_board_request = {
            "user_id": "nonexistent-user-id",
            "product_limit": 4
        }
        
        response = client.post("/api/v1/marketing/vision-boards/generate", json=vision_board_request)
        assert response.status_code == 404
    
    def test_invalid_email_template_type(self):
        """Test preview with invalid template type"""
        response = client.get("/api/v1/marketing/emails/templates/invalid_template/preview")
        assert response.status_code == 422  # Validation error
    
    def test_campaign_with_too_many_users(self):
        """Test email campaign with too many users (should be limited)"""
        # Create list of 101 user IDs (exceeds limit)
        user_ids = [f"user-{i}" for i in range(101)]
        
        campaign_data = {
            "user_ids": user_ids,
            "template_type": EmailTemplateType.WELCOME.value
        }
        
        response = client.post("/api/v1/marketing/campaigns/email", json=campaign_data)
        assert response.status_code == 400  # Should reject too many users
    
    def test_vision_board_with_different_limits(self):
        """Test vision board generation with different product limits"""
        # Test minimum limit
        vision_board_request = {
            "user_id": self.user_id,
            "product_limit": 4
        }
        
        response = client.post("/api/v1/marketing/vision-boards/generate", json=vision_board_request)
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) <= 4
        
        # Test maximum limit
        vision_board_request["product_limit"] = 16
        response = client.post("/api/v1/marketing/vision-boards/generate", json=vision_board_request)
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) <= 16