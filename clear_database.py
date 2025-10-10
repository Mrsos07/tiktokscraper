"""
Clear all data from database
"""
import asyncio
from sqlalchemy import select, delete
from app.models.database import get_db
from app.models.models import Job, Video, MonitoredAccount, ScheduledJob
from app.core.logging import log


async def clear_all_data():
    """Delete all data from all tables"""
    print("=" * 60)
    print("⚠️  CLEARING ALL DATABASE DATA")
    print("=" * 60)
    print()
    
    async for db in get_db():
        try:
            # Count records before deletion
            jobs_count = (await db.execute(select(Job))).scalars().all()
            videos_count = (await db.execute(select(Video))).scalars().all()
            monitored_count = (await db.execute(select(MonitoredAccount))).scalars().all()
            scheduled_count = (await db.execute(select(ScheduledJob))).scalars().all()
            
            print(f"Current records:")
            print(f"  - Jobs: {len(jobs_count)}")
            print(f"  - Videos: {len(videos_count)}")
            print(f"  - Monitored Accounts: {len(monitored_count)}")
            print(f"  - Scheduled Jobs: {len(scheduled_count)}")
            print()
            
            # Delete all data
            print("Deleting data...")
            
            # Delete in correct order (respect foreign keys)
            await db.execute(delete(Video))
            print("  ✅ Deleted all Videos")
            
            await db.execute(delete(Job))
            print("  ✅ Deleted all Jobs")
            
            await db.execute(delete(MonitoredAccount))
            print("  ✅ Deleted all Monitored Accounts")
            
            await db.execute(delete(ScheduledJob))
            print("  ✅ Deleted all Scheduled Jobs")
            
            await db.commit()
            
            print()
            print("=" * 60)
            print("✅ ALL DATA CLEARED SUCCESSFULLY!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(clear_all_data())
