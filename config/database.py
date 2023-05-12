from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from config.conf import settings

from app.models.base import Base

engine = create_async_engine(settings.DB_URL, future=True, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)


async def create_tables():
    """ Create tables instead of alembic migrations """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """ Getting db connection """
    async with async_session() as session:
        yield session
