from fastapi import APIRouter
from .auth import router as auth_router
from .boards import router as boards_router
from .tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(boards_router, prefix="/boards", tags=["boards"])
api_router.include_router(tasks_router, prefix="/boards", tags=["tasks"])
