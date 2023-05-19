from fastapi import APIRouter, Depends, BackgroundTasks

from config.database import AsyncSession, get_session

from app.services.profile.jwt import get_current_user
from app.services.profile.crud import (
    profile_create, jwt_create, jwt_refresh,
    send_reset_password, password_reset, send_excel,
    get_widget_url
)
from app.schemas.profile import (
    ProfileCreate, ProfileRetrieve,
    Tokens, RefreshToken, ProfileEmail,
    NewPassword, WidgetURL
)


profile_router = APIRouter()


@profile_router.post("/profile/create/", response_model=Tokens)
async def create_profile(
        profile: ProfileCreate,
        db: AsyncSession = Depends(get_session)
):
    return await profile_create(profile, db)


@profile_router.post("/token/", response_model=Tokens, status_code=200)
async def create_jwt(
        profile: ProfileCreate,
        db: AsyncSession = Depends(get_session)
):
    return await jwt_create(profile, db)


@profile_router.post("/refresh/token/", response_model=Tokens, status_code=200)
async def refresh_jwt(
        refresh_token: RefreshToken,
        db: AsyncSession = Depends(get_session)
):
    return await jwt_refresh(refresh_token, db)


@profile_router.get("/me/", response_model=ProfileRetrieve, status_code=200)
async def me(profile: ProfileRetrieve = Depends(get_current_user)):
    return profile


@profile_router.get("/profile/widget-url/", response_model=WidgetURL)
async def get_url(profile: ProfileRetrieve = Depends(get_current_user)):
    return await get_widget_url(profile)


@profile_router.post("/profile/send-reset-email/")
async def send_reset_password_email(
        background_tasks: BackgroundTasks,
        email: ProfileEmail,
        db: AsyncSession = Depends(get_session)
):
    return await send_reset_password(background_tasks, email, db)


@profile_router.post("/profile/new-password/", response_model=ProfileRetrieve)
async def profile_change_password(
    passwords: NewPassword,
    db: AsyncSession = Depends(get_session)
):
    return await password_reset(passwords, db)


@profile_router.get("/excel/")
async def get_excel(background_tasks: BackgroundTasks):
    return await send_excel(background_tasks)

