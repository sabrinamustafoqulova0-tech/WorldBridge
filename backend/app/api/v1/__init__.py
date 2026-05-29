from fastapi import APIRouter

from app.api.v1 import auth, programs, applications, users, articles

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(programs.router)
api_router.include_router(applications.router)
api_router.include_router(users.router)
api_router.include_router(articles.router)
