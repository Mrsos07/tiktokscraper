"""
Database management endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.database import init_db, engine, Base
from app.core.logging import log

router = APIRouter(prefix="/api/v1/database", tags=["database"])


@router.post("/init")
async def initialize_database():
    """
    Initialize/recreate database tables
    This will create any missing tables without dropping existing ones
    """
    try:
        log.info("Initializing database tables...")
        await init_db()
        log.info("Database tables initialized successfully")
        
        return {
            "success": True,
            "message": "Database tables initialized successfully"
        }
    except Exception as e:
        log.error(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recreate")
async def recreate_database():
    """
    Drop and recreate all database tables
    WARNING: This will delete all data!
    """
    try:
        log.warning("Recreating database - ALL DATA WILL BE LOST!")
        
        # Import models to register them
        from app.models import models  # noqa: F401
        
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            log.info("All tables dropped")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            log.info("All tables recreated")
        
        return {
            "success": True,
            "message": "Database recreated successfully",
            "warning": "All previous data has been deleted"
        }
    except Exception as e:
        log.error(f"Error recreating database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables")
async def list_tables():
    """
    List all database tables
    """
    try:
        from app.models import models  # noqa: F401
        
        tables = []
        for table_name, table in Base.metadata.tables.items():
            columns = [col.name for col in table.columns]
            tables.append({
                "name": table_name,
                "columns": columns
            })
        
        return {
            "success": True,
            "tables": tables,
            "total": len(tables)
        }
    except Exception as e:
        log.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))
