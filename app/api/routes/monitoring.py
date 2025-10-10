"""
Monitoring API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.scheduler.auto_scraper import auto_scraper
from app.core.logging import log

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


class MonitorAccountRequest(BaseModel):
    username: str


class MonitoringStatus(BaseModel):
    enabled: bool
    accounts: List[str]
    check_interval_minutes: int


@router.post("/accounts")
async def add_monitored_account(request: MonitorAccountRequest):
    """Add account to monitoring"""
    try:
        await auto_scraper.add_account(request.username)
        
        # Get updated list
        from sqlalchemy import select
        from app.models.database import get_db
        from app.models.models import MonitoredAccount
        
        async for db in get_db():
            result = await db.execute(
                select(MonitoredAccount).where(MonitoredAccount.enabled == True)
            )
            accounts = result.scalars().all()
            account_list = [acc.username for acc in accounts]
        
        return {
            "success": True,
            "message": f"Added @{request.username} to monitoring",
            "accounts": account_list
        }
    except Exception as e:
        log.error(f"Error adding account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/accounts/{username}")
async def remove_monitored_account(username: str):
    """Remove account from monitoring"""
    try:
        await auto_scraper.remove_account(username)
        
        # Get updated list
        from sqlalchemy import select
        from app.models.database import get_db
        from app.models.models import MonitoredAccount
        
        async for db in get_db():
            result = await db.execute(
                select(MonitoredAccount).where(MonitoredAccount.enabled == True)
            )
            accounts = result.scalars().all()
            account_list = [acc.username for acc in accounts]
        
        return {
            "success": True,
            "message": f"Removed @{username} from monitoring",
            "accounts": account_list
        }
    except Exception as e:
        log.error(f"Error removing account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts", response_model=List[str])
async def get_monitored_accounts():
    """Get list of monitored accounts"""
    from sqlalchemy import select
    from app.models.database import get_db
    from app.models.models import MonitoredAccount
    
    async for db in get_db():
        result = await db.execute(
            select(MonitoredAccount).where(MonitoredAccount.enabled == True)
        )
        accounts = result.scalars().all()
        return [acc.username for acc in accounts]


@router.get("/status", response_model=MonitoringStatus)
async def get_monitoring_status():
    """Get monitoring status"""
    return MonitoringStatus(
        enabled=auto_scraper.running,
        accounts=auto_scraper.monitored_accounts,
        check_interval_minutes=auto_scraper.check_interval // 60
    )


@router.post("/check-now")
async def trigger_check_now():
    """Manually trigger a check cycle"""
    try:
        import asyncio
        asyncio.create_task(auto_scraper.run_check_cycle())
        return {
            "success": True,
            "message": "Check cycle started"
        }
    except Exception as e:
        log.error(f"Error triggering check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
