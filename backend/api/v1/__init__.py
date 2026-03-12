from fastapi import APIRouter

from backend.api.v1 import auth, users, tenants, projects, reviews, oauth


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tenants.router)
api_router.include_router(projects.router)
api_router.include_router(reviews.router)
api_router.include_router(oauth.router)
