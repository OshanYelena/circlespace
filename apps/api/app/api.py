from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.friendships.router import router as friendships_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(friendships_router)
