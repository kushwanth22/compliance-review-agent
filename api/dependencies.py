"""
FastAPI dependency injection.
Provides DB session and settings to route handlers.
"""
from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionFactory
from config.settings import Settings, get_settings


async def get_session() -> AsyncGenerator[AsyncSession, None]:
      """Yield an async database session per request."""
      async with AsyncSessionFactory() as session:
                try:
                              yield session
                              await session.commit()
except Exception:
            await session.rollback()
            raise
finally:
            await session.close()


def get_app_settings(settings: Settings = Depends(get_settings)) -> Settings:
      """Inject application settings."""
      return settings
