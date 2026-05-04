"""
FastAPI application entry point for the portfolio service.

Creates the application instance, registers all routers, and
configures middleware. The lifespan context manager handles
startup and shutdown events — database connection pool
initialisation happens here before the first request is served.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown.
    Resources that require async initialisation (connection pools,
    background tasks) are set up here rather than at module import time.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print("Shutting down — closing database connections")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Portfolio management service for CryptoTrade Hub. "
        "Handles user accounts, asset holdings, and P&L tracking."
    ),
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc alternative
    lifespan=lifespan,
)

# CORS — in production this is restricted to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint used by Docker and Kubernetes probes.
    Returns service name and version — no database call is made
    so the endpoint remains available even during DB outages.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
