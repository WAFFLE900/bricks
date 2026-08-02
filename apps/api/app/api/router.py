from fastapi import APIRouter

from app.api.routes import auth, notifications, projects, records, search, tags, users
from app.collab import routes as collab

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(records.router, tags=["records"])
api_router.include_router(tags.router, tags=["tags"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(collab.router, tags=["collab"])
