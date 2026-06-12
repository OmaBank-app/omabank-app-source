from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.config import settings

# The Key Vault loader handles the fallback if KEY_VAULT_URL isn't set.
# Ensures it replaces standard postgresql:// with the asyncpg driver.
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if not DATABASE_URL:
    raise ValueError(
        "CRITICAL: DATABASE_URL is not configured. Cannot initialize database."
    )

# Initialize the async engine.
# For a 4GB node, we keep the pool size small to prevent memory exhaustion.
engine = create_async_engine(
    DATABASE_URL, echo=False, pool_size=5, max_overflow=10, pool_timeout=30
)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autocommit=False, autoflush=False
)

Base = declarative_base()


async def get_db():
    """Dependency injection for FastAPI routes to get a database session."""
    async with AsyncSessionLocal() as session:
        yield session
