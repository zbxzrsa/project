from fastapi import APIRouter

from backend.api.v1 import (
    auth,
    users,
    tenants,
    projects,
    reviews,
    oauth,
    analysis,
    dashboard,
    webhooks,
)


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tenants.router)
api_router.include_router(projects.router)
api_router.include_router(reviews.router)
api_router.include_router(oauth.router)
api_router.include_router(analysis.router)
api_router.include_router(dashboard.router)
api_router.include_router(webhooks.router)
