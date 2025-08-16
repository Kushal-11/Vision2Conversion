from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.marketing_service import marketing_service
from app.services.vision_board_service import vision_board_service
from app.services.user_data_service import user_data_service
from app.models.schemas import (
    EmailTemplate, EmailTemplateType, GeneratedEmail, PersonalizedEmailRequest,
    VisionBoardRequest, VisionBoard
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/emails/generate", response_model=GeneratedEmail)
async def generate_personalized_email(
    request: PersonalizedEmailRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized email content for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        generated_email = marketing_service.generate_personalized_email(db, request)
        return generated_email
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating personalized email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/emails/templates", response_model=List[EmailTemplate])
async def get_email_templates():
    """Get available email templates"""
    try:
        templates = marketing_service.get_available_templates()
        return templates
    except Exception as e:
        logger.error(f"Error getting email templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/emails/templates/{template_type}/preview")
async def preview_email_template(
    template_type: EmailTemplateType,
    sample_data: Optional[Dict[str, Any]] = None
):
    """Preview email template with sample data"""
    try:
        preview = marketing_service.preview_email_template(template_type, sample_data)
        return preview
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error previewing email template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/emails/template-types")
async def get_email_template_types():
    """Get available email template types"""
    return {
        "template_types": [template_type.value for template_type in EmailTemplateType]
    }


@router.post("/vision-boards/generate", response_model=VisionBoard)
async def generate_vision_board(
    request: VisionBoardRequest,
    db: Session = Depends(get_db)
):
    """Generate a personalized vision board for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        vision_board = vision_board_service.generate_vision_board(db, request)
        return vision_board
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating vision board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/vision-boards/themes")
async def get_vision_board_themes():
    """Get available vision board themes"""
    try:
        themes = vision_board_service.get_vision_board_themes()
        return {"themes": themes}
    except Exception as e:
        logger.error(f"Error getting vision board themes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/vision-boards/styles")
async def get_vision_board_styles():
    """Get available vision board style options"""
    try:
        styles = vision_board_service.get_style_options()
        return {"styles": styles}
    except Exception as e:
        logger.error(f"Error getting vision board styles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/campaigns/email")
async def create_email_campaign(
    user_ids: List[str],
    template_type: EmailTemplateType,
    additional_data: Dict[str, Any] = {},
    db: Session = Depends(get_db)
):
    """Create email campaign for multiple users"""
    try:
        if len(user_ids) > 100:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 users per campaign"
            )
        
        results = []
        failed_users = []
        
        for user_id in user_ids:
            try:
                # Verify user exists
                user = user_data_service.get_user_by_id(db, user_id)
                if not user:
                    failed_users.append({"user_id": user_id, "reason": "User not found"})
                    continue
                
                # Generate email
                request = PersonalizedEmailRequest(
                    user_id=user_id,
                    template_type=template_type,
                    additional_data=additional_data
                )
                
                generated_email = marketing_service.generate_personalized_email(db, request)
                results.append({
                    "user_id": user_id,
                    "email_subject": generated_email.subject,
                    "status": "generated"
                })
                
            except Exception as e:
                logger.warning(f"Failed to generate email for user {user_id}: {e}")
                failed_users.append({"user_id": user_id, "reason": str(e)})
        
        return {
            "message": "Email campaign created",
            "total_users": len(user_ids),
            "successful": len(results),
            "failed": len(failed_users),
            "results": results,
            "failed_users": failed_users
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating email campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )