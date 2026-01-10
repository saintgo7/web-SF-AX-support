"""API v1 router that combines all API routers."""
from fastapi import APIRouter

from src.app.api.v1 import auth, experts, questions, evaluation, applications, companies, matchings, admin, reports

api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(auth.router)

# Include expert management endpoints
api_router.include_router(experts.router)

# Include question management endpoints
api_router.include_router(questions.router)

# Include evaluation and grading endpoints
api_router.include_router(evaluation.router)

# Include application management endpoints
api_router.include_router(applications.router)

# Include company management endpoints
api_router.include_router(companies.router)
api_router.include_router(companies.demands_router)

# Include matching endpoints
api_router.include_router(matchings.router)

# Include admin endpoints
api_router.include_router(admin.router)

# Include report endpoints
api_router.include_router(reports.router)
