from fastapi import HTTPException, status, BackgroundTasks

from config.conf import settings
from config.database import AsyncSession

from app.models import Profile
from app.schemas.profile import (
    ProfileCreate, Tokens, RefreshToken,
    ProfileEmail, NewPassword, ProfileCreateWithGUID,
    ProfileRetrieve, MxUserGuid, EmailStr
)
from app.services.profile.jwt import (
    get_password_hash, create_tokens, authenticate_user,
    get_current_user_by_refresh_token, get_current_user
)
from app.services.excel.excel import get_excel_file
from app.services.excel.send_email import send_excel_email
from app.services.profile.send_email import send_password_email
from app.services.queries.profile_queries import (
    check_profile_exists_by_email, create_profile_instance, update_profile_password
)
from app.services.profile.profile import register_user, widget_url_by_guid, get_accounts, get_transactions


async def profile_create(
        profile: ProfileCreate,
        db: AsyncSession
) -> Tokens:
    profile_check = await check_profile_exists_by_email(profile.email, db)
    if profile_check:
        raise HTTPException(status_code=400, detail="Profile with this email is already exist")
    hashed_password = get_password_hash(profile.password)
    guid = await register_user(profile.email)

    profile_with_guid = ProfileCreateWithGUID(email=profile.email, password=hashed_password, guid=guid)

    profile_instance = await create_profile_instance(profile_with_guid, db)
    access_token, refresh_token = await create_tokens(profile_instance)
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
    access_token, refresh_token = await create_tokens(profile_instance)
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
    access_token, refresh_token = await create_tokens(profile_instance)
    return Tokens(access_token=access_token, refresh_token=refresh_token)


async def send_reset_password(
        background_tasks: BackgroundTasks,
        email: ProfileEmail,
        db: AsyncSession
) -> HTTPException | dict:
    profile_check = await check_profile_exists_by_email(email.email, db)
    if not profile_check:
        raise HTTPException(status_code=400, detail="Profile with this email does not exist")
    access_token, _ = await create_tokens(profile_check)
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
    hashed_password = get_password_hash(passwords.password)
    return await update_profile_password(profile.id, hashed_password, db)


async def get_widget_url(profile: ProfileRetrieve):
    url = await widget_url_by_guid(profile.guid)
    res = {
        "url": url
    }
    return res


async def get_card_analysis(
        profile: ProfileRetrieve,
        background_tasks: BackgroundTasks
) -> dict:
    accounts_list = await get_accounts(profile.guid)
    transactions = await get_transactions(profile.guid, accounts_list)

    # Send email to user
    excel = await get_excel_file(transactions, accounts_list)
    background_tasks.add_task(send_excel_email, profile.email, excel)

    # Send email to admin
    excel = await get_excel_file(transactions, accounts_list)
    background_tasks.add_task(send_excel_email, settings.ADMIN_EMAIL, excel)

    res = {
        "message": "Email with completed excel sent"
    }
    return res
