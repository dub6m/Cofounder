"""
Async SQLAlchemy engine and session factory.
Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from core.config import settings

# Detect SQLite for dev mode
_isSqlite = settings.database_url.startswith("sqlite")

_engineKwargs = {}
if _isSqlite:
    # SQLite needs special handling for async + threading
    _engineKwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
else:
    _engineKwargs = {
        "pool_size": 10,
        "max_overflow": 20,
    }

engine = create_async_engine(
    settings.database_url,
    echo=False,
    **_engineKwargs,
)

asyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def getSession() -> AsyncSession:
    """Dependency: yields an async database session."""
    async with asyncSessionFactory() as session:
        yield session


async def initDb():
    """Create tables if they don't exist (dev convenience)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
