"""
Cleanup API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.scheduler.cleanup_task import cleanup_task
from app.core.logging import log

router = APIRouter(prefix="/api/v1/cleanup", tags=["cleanup"])


class CleanupStatus(BaseModel):
    running: bool
    max_age_hours: int
    cleanup_interval_seconds: int


@router.get("/status", response_model=CleanupStatus)
async def get_cleanup_status():
    """Get cleanup task status"""
    return CleanupStatus(
        running=cleanup_task.running,
        max_age_hours=cleanup_task.max_age_hours,
        cleanup_interval_seconds=cleanup_task.cleanup_interval
    )


@router.post("/run-now")
async def trigger_cleanup_now():
    """Manually trigger cleanup cycle"""
    try:
        import asyncio
        asyncio.create_task(cleanup_task.run_cleanup())
        return {
            "success": True,
            "message": "Cleanup cycle started"
        }
    except Exception as e:
        log.error(f"Error triggering cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))
