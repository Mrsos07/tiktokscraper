"""
Initialize database tables
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db
from app.core.logging import log


async def main():
    """Initialize database"""
    try:
        log.info("Initializing database...")
        await init_db()
        log.info("Database initialized successfully!")
        
    except Exception as e:
        log.error(f"Error initializing database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
