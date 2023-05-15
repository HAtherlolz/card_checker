from fastapi import HTTPException, status, BackgroundTasks

from config.database import AsyncSession

from app.models import Profile
from app.schemas.profile import ProfileCreate, Tokens, RefreshToken, ProfileEmail, NewPassword
from app.services.profile.jwt import (
    get_password_hash, create_tokens, authenticate_user,
    get_current_user_by_refresh_token, get_current_user
)
from app.services.profile.send_email import send_password_email
from app.services.queries.profile_queries import (
    check_profile_exists_by_email, create_profile_instance, update_profile_password
)


async def profile_create(
        profile: ProfileCreate,
        db: AsyncSession
) -> Tokens:
    profile_check = await check_profile_exists_by_email(profile.email, db)
    if profile_check:
        raise HTTPException(status_code=400, detail="Profile with this email is already exist")
    profile.password = get_password_hash(profile.password)
    profile_instance = await create_profile_instance(profile, db)
    access_token, refresh_token = create_tokens(profile_instance)
    return Tokens(access_token=access_token, refresh_token=refresh_token)


async def jwt_create(
        profile: ProfileCreate,
        db: AsyncSession
) -> Tokens:
    profile_instance = await authenticate_user(profile.email, profile.password, db)
    if not profile_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, refresh_token = create_tokens(profile_instance)
    return Tokens(access_token=access_token, refresh_token=refresh_token)


async def jwt_refresh(
        refresh_token: RefreshToken,
        db: AsyncSession
) -> Tokens:
    profile_instance = await get_current_user_by_refresh_token(refresh_token.refresh_token, db)
    if not profile_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, refresh_token = create_tokens(profile_instance)
    return Tokens(access_token=access_token, refresh_token=refresh_token)


async def send_reset_password(
        background_tasks: BackgroundTasks,
        email: ProfileEmail,
        db: AsyncSession
) -> HTTPException | dict:
    profile_check = await check_profile_exists_by_email(email.email, db)
    if not profile_check:
        raise HTTPException(status_code=400, detail="Profile with this email is already exist")
    access_token, _ = create_tokens(profile_check)
    background_tasks.add_task(send_password_email, email.email, access_token)
    return {"message": "The email for with link to reset password successfully send"}


async def password_reset(
        passwords: NewPassword,
        db: AsyncSession
) -> Profile | HTTPException:
    if passwords.password != passwords.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The passwords are different"
        )
    profile = await get_current_user(passwords.token)
    if isinstance(profile, bool):
        raise HTTPException(status_code=400, detail="Invalid token")
    hashed_password = get_password_hash(profile.password)
    return await update_profile_password(profile.id, hashed_password, db)