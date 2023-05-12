from datetime import timedelta, datetime

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext

from config.conf import settings
from config.database import AsyncSession, async_session

from app.services.queries.profile_queries import check_profile_exists_by_email
from app.models.profile import Profile
from app.schemas.profile import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Profile | bool:
    profile = await check_profile_exists_by_email(email, db)
    if not profile:
        return False
    if not verify_password(password, profile.password):
        return False
    return profile


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Profile:
    async with async_session() as db:
        return await get_user_instance(token, db)


async def get_current_user_by_refresh_token(token: str, db: AsyncSession) -> Profile:
    return await get_user_instance(token, db)


async def get_user_instance(token: str, db: AsyncSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await check_profile_exists_by_email(token_data.email, db)
    if user is None:
        raise credentials_exception
    return user


def create_tokens(profile: Profile) -> tuple:
    to_access_encode = {
        "sub": profile.email,
        "user_id": profile.id
    }
    to_refresh_encode = {
        "sub": profile.email,
        "user_id": profile.id
    }
    access_expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 24 * 7)
    refresh_expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 24 * 30)
    to_access_encode.update({"exp": access_expire})
    to_access_encode.update({"token_type": "access"})
    to_refresh_encode.update({"exp": refresh_expire})
    to_refresh_encode.update({"token_type": "refresh"})
    access_jwt = jwt.encode(to_access_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    refresh_jwt = jwt.encode(to_refresh_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_jwt, refresh_jwt


