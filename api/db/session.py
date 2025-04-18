from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from redis import asyncio as aioredis
from typing import AsyncGenerator

from api.config import settings

# PostgreSQL engine and session
engine = create_async_engine(
    settings.DATABASE_URL.replace('postgresql', 'postgresql+asyncpg'),
    echo=settings.DEBUG,
    future=True,
)
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()

# Redis connection pool
redis_pool = None

async def init_db():
    """Initialize database connections."""
    global redis_pool
    
    # Create Redis connection pool
    redis_pool = aioredis.ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=10,
        decode_responses=True,
    )
    
    # Create all tables in the database
    async with engine.begin() as conn:
        if settings.ENVIRONMENT == "development":
            # In development, we can optionally recreate tables
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis():
    """Get Redis connection."""
    if redis_pool is None:
        await init_db()
    
    async with aioredis.Redis(connection_pool=redis_pool) as redis:
        yield redis