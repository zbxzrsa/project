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
    api_keys,
    audit_logs,
    llm_settings,
    admin,
    branches,
    feedback,
    compliance,
    metrics,
    tasks,
    repositories,
    settings,
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
api_router.include_router(api_keys.router)
api_router.include_router(audit_logs.router)
api_router.include_router(llm_settings.router)
api_router.include_router(admin.router)
api_router.include_router(branches.router)
api_router.include_router(feedback.router)
api_router.include_router(compliance.router)
api_router.include_router(metrics.router)
api_router.include_router(tasks.router)
api_router.include_router(repositories.router)
api_router.include_router(settings.router)
