"""
Structured logging configuration using structlog.
JSON format for production/POC, console format for local dev.
"""
import logging
import sys
import structlog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
      from config.settings import Settings


def setup_logging(settings: "Settings") -> None:
      """Configure structlog with JSON or console renderer based on environment."""

    shared_processors = [
              structlog.contextvars.merge_contextvars,
              structlog.processors.add_log_level,
              structlog.processors.StackInfoRenderer(),
              structlog.dev.set_exc_info,
              structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.log_format == "json":
              # JSON output for POC/production - parseable by Azure Monitor, Datadog etc.
              renderer = structlog.processors.JSONRenderer()
else:
          # Pretty console output for local development
          renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
              processors=shared_processors + [
                            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
              ],
              logger_factory=structlog.stdlib.LoggerFactory(),
              wrapper_class=structlog.stdlib.BoundLogger,
              cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
              foreign_pre_chain=shared_processors,
              processors=[
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            renderer,
              ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Suppress noisy third-party loggers
    for noisy in ["httpx", "chromadb", "uvicorn.access"]:
              logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
      """Get a named structured logger."""
      return structlog.get_logger(name)
