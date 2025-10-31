import sys
import asyncio

# Fix for Python 3.13 on Windows - must be set before any async operations
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import log
from app.models.database import init_db
from app.api.routes import jobs, videos, scheduler, stats, cleanup, database
from app.middleware import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    log.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Initialize database
    try:
        await init_db()
        log.info("Database initialized")
    except Exception as e:
        log.error(f"Database initialization failed: {e}")
        raise
    
    # Start cleanup task
    from app.scheduler.cleanup_task import cleanup_task
    asyncio.create_task(cleanup_task.start())
    log.info("Cleanup Task started (deletes files older than 24 hours)")
    
    # Create required directories
    settings.local_storage_path_obj.mkdir(parents=True, exist_ok=True)
    settings.credentials_path.mkdir(parents=True, exist_ok=True)
    
    log.info("Application startup complete")
    
    yield
    # Shutdown
    log.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="TikTok Video Scraper & Downloader with Google Drive Integration",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
    burst=settings.RATE_LIMIT_BURST
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    log.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(scheduler.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(cleanup.router)
app.include_router(database.router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/stats/health"
    }


# Health check
@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
