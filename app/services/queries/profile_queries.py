from sqlalchemy import select, update

from config.database import AsyncSession

from app.models import Profile
from app.schemas.profile import ProfileCreate


async def check_profile_exists_by_email(
        email: str,
        db: AsyncSession
) -> Profile | None:
    profile = await db.execute(
        select(Profile).where(Profile.email == email)
    )
    return profile.scalar_one_or_none()


async def create_profile_instance(
        profile: ProfileCreate,
        db: AsyncSession
) -> Profile:
    new_profile = Profile(**profile.dict())
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile


async def update_profile_password(
        profile_id: int,
        hashed_password: str,
        db: AsyncSession
) -> Profile:
    update_pass = await db.execute(
        update(Profile).where(Profile.id == profile_id).values(password=hashed_password).returning(Profile)
    )
    await db.commit()
    return update_pass.scalar_one()

