from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.db.models import Base

settings = get_settings()

if settings.database_url is None:
    msg = "DATABASE_URL must be set before importing src.db.connection"
    raise RuntimeError(msg)

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False
)


async def init_db() -> None:
    """Create the vector extension and all tables on startup."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency-injectable async session."""
    async with AsyncSessionFactory() as session:
        yield session
