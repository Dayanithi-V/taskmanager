import logging
import os

from .config import APPLICATIONINSIGHTS_CONNECTION_STRING

logger = logging.getLogger(__name__)


def configure_application_insights(app) -> None:
    """
    Enable Azure Monitor OpenTelemetry + FastAPI auto-instrumentation when
    APPLICATIONINSIGHTS_CONNECTION_STRING is set.
    Safe no-op when unset or dependencies unavailable.
    """
    conn = APPLICATIONINSIGHTS_CONNECTION_STRING.strip()
    if not conn:
        logger.info("Application Insights disabled (no connection string).")
        return

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        configure_azure_monitor(connection_string=conn)
        FastAPIInstrumentor.instrument_app(app)
        logger.info("Application Insights OpenTelemetry instrumentation enabled.")
    except Exception as exc:  # pragma: no cover - optional integration path
        logger.warning("Could not enable Application Insights: %s", exc)


def configure_logging() -> None:
    """Consistent structured-ish logging for containers and App Service."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
