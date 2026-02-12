from fastapi import APIRouter

from app.api.v1.endpoints import assets, files, health, render_tasks, templates

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_v1_router.include_router(render_tasks.router, prefix="/render", tags=["render"])
api_v1_router.include_router(files.router, prefix="/files", tags=["files"])
api_v1_router.include_router(templates.router, prefix="/templates", tags=["templates"])
