from fastapi import APIRouter

from app.endpoints.v1 import profile

api_router = APIRouter()

api_router.include_router(profile.profile_router, prefix='/api/v1', tags=["profiles"])

