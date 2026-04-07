"""
Async SQLAlchemy session management.
POC 0: SQLite via aiosqlite (zero cost, local file)
POC 1: PostgreSQL via asyncpg (swap DATABASE_URL env var)
"""
from __future__ import annotations
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from db.base import Base
from config.settings import get_settings

settings = get_settings()

# Create async engine
# POC 0: sqlite+aiosqlite:///./data/compliance.db
# POC 1: postgresql+asyncpg://user:pass@host/compliance
engine = create_async_engine(
      settings.database_url,
      echo=settings.is_local,  # Log SQL in local dev only
      future=True,
      # SQLite-specific: check_same_thread=False for async
      connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

AsyncSessionFactory = async_sessionmaker(
      bind=engine,
      class_=AsyncSession,
      expire_on_commit=False,
      autocommit=False,
      autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
      """FastAPI dependency - yields an async DB session."""
      async with AsyncSessionFactory() as session:
                try:
                              yield session
                              await session.commit()
except Exception:
            await session.rollback()
            raise
finally:
            await session.close()


async def init_db() -> None:
      """
          Create all database tables on startup.
              Safe to call multiple times - uses CREATE TABLE IF NOT EXISTS.
                  """
      async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
