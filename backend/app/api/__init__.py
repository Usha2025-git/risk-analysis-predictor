"""API routes package."""
from fastapi import APIRouter

from backend.app.api.routes import auth, projects, risks, resources, analytics

# Create main router
api_router = APIRouter()

# Include route modules with prefixes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"]
)

api_router.include_router(
    risks.router,
    prefix="/risks",
    tags=["Risks"]
)

api_router.include_router(
    resources.router,
    prefix="/resources",
    tags=["Resources"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

__all__ = ["api_router"]
