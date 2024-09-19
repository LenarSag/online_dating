from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base


async_engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3', echo=True)
# async_engine = create_async_engine(
#     'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres', echo=True
# )
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def init_models():
    async with async_engine.begin() as conn:
        existing_tables = await conn.run_sync(Base.metadata.reflect)
        if not existing_tables:
            await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
