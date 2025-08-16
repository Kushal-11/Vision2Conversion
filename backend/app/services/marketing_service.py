from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from jinja2 import Template, Environment, BaseLoader
from app.services.recommendation_service import recommendation_service
from app.services.user_data_service import user_data_service
from app.services.user_interest_service import user_interest_service
from app.services.product_service import product_service
from app.models.schemas import (
    EmailTemplate, EmailTemplateType, GeneratedEmail, 
    PersonalizedEmailRequest, User, Recommendation
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketingService:
    """Service for generating personalized marketing content"""
    
    def __init__(self):
        self.recommendation_service = recommendation_service
        self.user_service = user_data_service
        self.interest_service = user_interest_service
        self.product_service = product_service
        self.jinja_env = Environment(loader=BaseLoader())
        self._init_default_templates()
    
    def _init_default_templates(self):
        """Initialize default email templates"""
        self.default_templates = {
            EmailTemplateType.PERSONALIZED_RECOMMENDATIONS: EmailTemplate(
                id="personalized_recs_v1",
                name="Personalized Product Recommendations",
                template_type=EmailTemplateType.PERSONALIZED_RECOMMENDATIONS,
                subject_template="{{user_name}}, discover products perfect for you!",
                html_template="""
                <html>
                <head><title>Personalized Recommendations</title></head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50;">Hi {{user_name}}!</h1>
                        <p>Based on your interests in <strong>{{top_interests}}</strong>, we've curated these special recommendations just for you:</p>
                        
                        <div style="margin: 30px 0;">
                            {% for rec in recommendations %}
                            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; display: flex; align-items: center;">
                                {% if rec.product.image_url %}
                                <img src="{{rec.product.image_url}}" alt="{{rec.product.name}}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px; margin-right: 15px;">
                                {% endif %}
                                <div>
                                    <h3 style="margin: 0 0 5px 0; color: #34495e;">{{rec.product.name}}</h3>
                                    <p style="margin: 0 0 5px 0; color: #7f8c8d;">{{rec.product.description[:100]}}...</p>
                                    <p style="margin: 0; font-weight: bold; color: #e74c3c;">${{rec.product.price}}</p>
                                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #95a5a6;">{{rec.reason}}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Shop Now</a>
                        </div>
                        
                        <p style="font-size: 12px; color: #7f8c8d; text-align: center;">
                            This email was generated based on your personal shopping preferences and interests.
                        </p>
                    </div>
                </body>
                </html>
                """,
                text_template="""
                Hi {{user_name}}!
                
                Based on your interests in {{top_interests}}, here are our recommendations for you:
                
                {% for rec in recommendations %}
                • {{rec.product.name}} - ${{rec.product.price}}
                  {{rec.product.description[:100]}}...
                  Reason: {{rec.reason}}
                  
                {% endfor %}
                
                Happy shopping!
                """,
                variables=["user_name", "top_interests", "recommendations"]
            ),
            
            EmailTemplateType.WELCOME: EmailTemplate(
                id="welcome_v1",
                name="Welcome Email",
                template_type=EmailTemplateType.WELCOME,
                subject_template="Welcome to our store, {{user_name}}!",
                html_template="""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50;">Welcome {{user_name}}!</h1>
                        <p>We're excited to have you join our community of smart shoppers.</p>
                        <p>Here are some popular products to get you started:</p>
                        
                        <div style="margin: 30px 0;">
                            {% for rec in recommendations %}
                            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0;">
                                <h3 style="color: #34495e;">{{rec.product.name}}</h3>
                                <p style="color: #7f8c8d;">{{rec.product.description[:100]}}...</p>
                                <p style="font-weight: bold; color: #e74c3c;">${{rec.product.price}}</p>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Start Shopping</a>
                        </div>
                    </div>
                </body>
                </html>
                """,
                text_template="""
                Welcome {{user_name}}!
                
                We're excited to have you join our community.
                
                Here are some popular products to explore:
                {% for rec in recommendations %}
                • {{rec.product.name}} - ${{rec.product.price}}
                {% endfor %}
                
                Happy shopping!
                """,
                variables=["user_name", "recommendations"]
            ),
            
            EmailTemplateType.INTEREST_BASED: EmailTemplate(
                id="interest_based_v1",
                name="Interest-Based Recommendations",
                template_type=EmailTemplateType.INTEREST_BASED,
                subject_template="{{user_name}}, new {{interest_category}} items you'll love!",
                html_template="""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50;">Perfect {{interest_category}} finds for you!</h1>
                        <p>Hi {{user_name}}, we noticed you love {{interest_category}}. Check out these new arrivals:</p>
                        
                        <div style="margin: 30px 0;">
                            {% for rec in recommendations %}
                            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0;">
                                <h3 style="color: #34495e;">{{rec.product.name}}</h3>
                                <p style="color: #7f8c8d;">{{rec.product.description[:100]}}...</p>
                                <p style="font-weight: bold; color: #e74c3c;">${{rec.product.price}}</p>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </body>
                </html>
                """,
                text_template="""
                Perfect {{interest_category}} finds for you!
                
                Hi {{user_name}}, we noticed you love {{interest_category}}.
                
                Check out these new arrivals:
                {% for rec in recommendations %}
                • {{rec.product.name}} - ${{rec.product.price}}
                {% endfor %}
                """,
                variables=["user_name", "interest_category", "recommendations"]
            )
        }
    
    def generate_personalized_email(self, db: Session, request: PersonalizedEmailRequest) -> GeneratedEmail:
        """Generate personalized email content for a user"""
        try:
            # Get user information
            user = self.user_service.get_user_by_id(db, request.user_id)
            if not user:
                raise ValueError(f"User {request.user_id} not found")
            
            # Get user interests and recommendations
            interests = self.interest_service.get_user_interests(db, request.user_id, 10)
            recommendations = self.recommendation_service.get_personalized_recommendations(
                db, request.user_id, request.recommendations_limit
            )
            
            # Get product details for recommendations
            enriched_recommendations = []
            for rec in recommendations:
                product = self.product_service.get_product_by_id(db, rec.product_id)
                if product:
                    enriched_rec = {
                        "product": product,
                        "score": rec.score,
                        "reason": rec.reason,
                        "category": rec.category
                    }
                    enriched_recommendations.append(enriched_rec)
            
            # Prepare personalization data
            personalization_data = self._prepare_personalization_data(
                user, interests, enriched_recommendations, request.additional_data
            )
            
            # Get template and generate content
            template = self.default_templates.get(request.template_type)
            if not template:
                raise ValueError(f"Template type {request.template_type} not found")
            
            subject = self._render_template(template.subject_template, personalization_data)
            html_content = self._render_template(template.html_template, personalization_data)
            text_content = self._render_template(template.text_template, personalization_data)
            
            generated_email = GeneratedEmail(
                user_id=request.user_id,
                template_type=request.template_type,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                recommendations=recommendations,
                personalization_data=personalization_data
            )
            
            logger.info(f"Generated {request.template_type} email for user {request.user_id}")
            return generated_email
        
        except Exception as e:
            logger.error(f"Error generating personalized email: {e}")
            raise
    
    def _prepare_personalization_data(
        self, 
        user: User, 
        interests: List[Any], 
        recommendations: List[Dict[str, Any]], 
        additional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for email personalization"""
        # Extract user name from email or profile
        user_name = user.profile_data.get("name", user.email.split("@")[0].title())
        
        # Get top interest categories
        top_interests = []
        if interests:
            interest_categories = list(set([i.interest_category.value for i in interests[:3]]))
            top_interests = [cat.replace("_", " ").title() for cat in interest_categories]
        
        data = {
            "user_id": user.id,
            "user_name": user_name,
            "user_email": user.email,
            "top_interests": ", ".join(top_interests) if top_interests else "various categories",
            "interest_category": top_interests[0] if top_interests else "general",
            "recommendations": recommendations,
            "current_date": datetime.now().strftime("%B %d, %Y"),
            "total_recommendations": len(recommendations)
        }
        
        # Add additional data
        data.update(additional_data)
        
        return data
    
    def _render_template(self, template_string: str, data: Dict[str, Any]) -> str:
        """Render Jinja2 template with provided data"""
        try:
            template = self.jinja_env.from_string(template_string)
            return template.render(**data)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            raise ValueError(f"Template rendering failed: {e}")
    
    def get_available_templates(self) -> List[EmailTemplate]:
        """Get list of available email templates"""
        return list(self.default_templates.values())
    
    def preview_email_template(self, template_type: EmailTemplateType, sample_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Preview email template with sample data"""
        template = self.default_templates.get(template_type)
        if not template:
            raise ValueError(f"Template type {template_type} not found")
        
        # Use sample data if provided, otherwise use defaults
        if not sample_data:
            sample_data = {
                "user_name": "John Doe",
                "user_email": "john@example.com",
                "top_interests": "Technology, Fashion, Books",
                "interest_category": "Technology",
                "recommendations": [
                    {
                        "product": {
                            "name": "Sample Product",
                            "description": "This is a sample product description for preview purposes.",
                            "price": 99.99,
                            "image_url": "https://via.placeholder.com/80"
                        },
                        "reason": "Based on your interest in technology"
                    }
                ],
                "current_date": datetime.now().strftime("%B %d, %Y")
            }
        
        try:
            subject = self._render_template(template.subject_template, sample_data)
            html_content = self._render_template(template.html_template, sample_data)
            text_content = self._render_template(template.text_template, sample_data)
            
            return {
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content
            }
        except Exception as e:
            logger.error(f"Error previewing template: {e}")
            raise


# Create service instance
marketing_service = MarketingService()