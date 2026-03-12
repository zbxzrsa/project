from fastapi import APIRouter

from backend.api.v1 import auth, users, tenants, projects


api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tenants.router)
api_router.include_router(projects.router)
