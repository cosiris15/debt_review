"""
Debt Review System - FastAPI Entry Point

Main API server that exposes the debt review workflow as REST APIs.
Uses async task pattern for long-running operations.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import (
    projects_router,
    creditors_router,
    tasks_router,
    tools_router,
    reports_router
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="API for processing and reviewing debt claims in bankruptcy proceedings",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router, prefix="/api")
app.include_router(creditors_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(tools_router, prefix="/api")
app.include_router(reports_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "api": "running",
            "database": "configured" if settings.SUPABASE_URL else "not_configured",
            "llm": "configured" if settings.DEEPSEEK_API_KEY else "not_configured"
        }
    }


@app.get("/api/status")
async def api_status():
    """API status with running tasks info."""
    from app.services.task_runner import TaskRunner

    running_tasks = TaskRunner.get_running_tasks()

    return {
        "status": "running",
        "running_tasks_count": len(running_tasks),
        "running_task_ids": running_tasks,
        "max_concurrent_tasks": settings.MAX_CONCURRENT_TASKS
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
