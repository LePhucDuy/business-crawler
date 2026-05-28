from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import health, business_lookup
from app.core.config import settings
from app.core.browser_manager import browser_manager
from app.core.rate_limit import RateLimitMiddleware
import app.crawlers.providers  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await browser_manager.start()
    yield
    # Shutdown
    await browser_manager.stop()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

app.add_middleware(RateLimitMiddleware)

app.include_router(health.router, tags=["Health"])
app.include_router(business_lookup.router, prefix="/api/v1/business", tags=["Business Lookup"])
