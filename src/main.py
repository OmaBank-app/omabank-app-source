import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Observability Integrations
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from src.core.config import settings
from src.core.security import load_dynamic_secrets
from src.domains.ledger.api import router as ledger_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: Zero-Trust initialization before accepting traffic."""
    logger.info(f"Booting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode...")

    # Securely load credentials from Key Vault (or .env if local)
    load_dynamic_secrets()

    # Initialize the database engine (Instrumented for tracing)
    from src.core.database import engine

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

    logger.info("OmaBank Core is ready to process your financial transactions.")
    yield

    logger.info("Initiating graceful shutdown...")
    await engine.dispose()


# Initialize the API
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=settings.API_V1_STR + "/docs",
    openapi_url=settings.API_V1_STR + "/openapi.json",
)

# Attach the Ledger Domain
app.include_router(ledger_router, prefix=settings.API_V1_STR)

# Attach OpenTelemetry to trace every HTTP request
FastAPIInstrumentor.instrument_app(app)

# Mount static files for serving HTML, CSS, images
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/", response_class=FileResponse, tags=["Pages"])
async def welcome_page():
    """Serve the welcome landing page with custom background."""
    return "static/index.html"


@app.get("/about", response_class=FileResponse, tags=["Pages"])
async def about_page():
    """Serve the about page with custom background."""
    return "static/about.html"
