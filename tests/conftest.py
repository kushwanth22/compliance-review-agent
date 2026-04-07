"""
pytest fixtures for unit and integration tests.
Uses async fixtures and in-memory SQLite for zero-cost testing.
"""
from __future__ import annotations
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from db.base import Base
from api.app import create_app
from api.dependencies import get_session

# ── Test Database ────────────────────────────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
      TEST_DB_URL,
      connect_args={"check_same_thread": False},
)

TestSessionFactory = async_sessionmaker(
      bind=test_engine,
      class_=AsyncSession,
      expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session")
async def test_db():
      """Create all tables in in-memory SQLite for the test session."""
      async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            yield
    async with test_engine.begin() as conn:
              await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_db) -> AsyncSession:
      """Provide a clean async DB session per test with rollback."""
    async with TestSessionFactory() as session:
              yield session
              await session.rollback()


# ── FastAPI Test Client ───────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession) -> AsyncClient:
      """Async test client with DB session override."""
    app = create_app()

    async def override_get_session():
              yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
              transport=ASGITransport(app=app),
              base_url="http://testserver",
    ) as client:
              yield client

    app.dependency_overrides.clear()


# ── Sample Assets ─────────────────────────────────────────────────────────────
@pytest.fixture
def sample_text_content() -> str:
      """Sample creative asset text for testing."""
    return """
        Microsoft Azure - The Cloud Platform for Modern Business

            Get started today with free tier services.
                Learn more at microsoft.com/azure

                    Note: Pricing subject to change. See terms and conditions.
                        """


@pytest.fixture
def sample_asset_metadata() -> dict:
      """Sample asset metadata for testing."""
    return {
              "filename": "test_banner.png",
              "file_type": "image/png",
              "file_size_bytes": 102400,
              "width": 1200,
              "height": 628,
              "campaign": "Azure Free Tier Q2 2026",
    }


@pytest.fixture
def mock_retrieved_context() -> str:
      """Mock RAG-retrieved compliance guidance for testing."""
    return """
        [Source: brand_guidelines.md | Section: Logo Usage | Relevance: 0.95]
            The Microsoft logo must always appear on a white or light background.
                Minimum logo size is 120px wide for digital assets.
                    Do not modify, rotate, or add effects to the Microsoft logo.

                        ---

                            [Source: legal_cela_guidelines.md | Section: Disclaimers | Relevance: 0.88]
                                All pricing claims must include a disclaimer: "Pricing subject to change."
    Free tier claims must link to full terms at microsoft.com/terms.
        Claims about availability must specify geographic limitations.
            """
