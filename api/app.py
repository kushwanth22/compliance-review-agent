"""
FastAPI application factory.
POC 0: Run locally via docker compose up
POC 1: Deploy to Azure Container Apps via GitHub Actions
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from config.logging_config import setup_logging, get_logger
from api.middleware.audit_logger import AuditLogMiddleware
from api.middleware.error_handler import register_exception_handlers
from api.routes import assets, reviews, reports
from db.session import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
      """Application startup and shutdown lifecycle."""
      settings = get_settings()
      setup_logging(settings)

    logger.info(
              "compliance_agent_starting",
              env=settings.env,
              llm_model=settings.llm_model,
              vector_store=settings.vector_store,
              database_url=settings.database_url.split("///")[0],  # Don't log full path
    )

    # Initialize database tables (creates SQLite file on first run)
    await init_db()

    logger.info("compliance_agent_ready", host=settings.api_host, port=settings.api_port)

    yield

    logger.info("compliance_agent_shutting_down")


def create_app() -> FastAPI:
      """Create and configure the FastAPI application."""
      settings = get_settings()

    app = FastAPI(
              title="Compliance Review Agent",
              description=(
                            "POC 0 - Automated multi-domain compliance review for Microsoft Global Ads. "
                            "Evaluates creative assets (PNG, JPEG, GIF, HTML5, MP4, PDF, DOCX, PPTX) "
                            "against Brand, Legal/CELA, Accessibility, Global Readiness, and "
                            "Product Marketing standards. Produces pass/fail decisions with severity "
                            "scoring, rationale, and human escalation triggers."
              ),
              version="0.1.0",
              docs_url="/docs",
              redoc_url="/redoc",
              lifespan=lifespan,
    )

    # CORS (restrict in production)
    app.add_middleware(
              CORSMiddleware,
              allow_origins=["*"] if settings.is_local else ["https://your-domain.com"],
              allow_methods=["*"],
              allow_headers=["*"],
    )

    # Audit logging middleware - logs every review request/response
    app.add_middleware(AuditLogMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(assets.router, prefix="/api/v1", tags=["Assets"])
    app.include_router(reviews.router, prefix="/api/v1", tags=["Reviews"])
    app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])

    @app.get("/health", tags=["Health"])
    async def health_check():
              """Health check endpoint for container readiness probes."""
              return {
                  "status": "ok",
                  "env": settings.env,
                  "llm_model": settings.llm_model,
                  "vector_store": settings.vector_store,
              }

    return app


app = create_app()


if __name__ == "__main__":
      import uvicorn
      settings = get_settings()
      uvicorn.run(
          "api.app:app",
          host=settings.api_host,
          port=settings.api_port,
          reload=settings.api_reload,
      )
