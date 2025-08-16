from fastapi import APIRouter
from app.api.v1.endpoints import users, products, recommendations, interests, marketing, cache, analytics

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(interests.router, prefix="/interests", tags=["interests"])
api_router.include_router(marketing.router, prefix="/marketing", tags=["marketing"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@api_router.get("/")
async def api_root():
    return {"message": "Personalized Marketing API v1"}