"""Global scheduler instance for the application."""
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def set_scheduler(scheduler: AsyncIOScheduler) -> None:
    """Set the global scheduler instance.

    Args:
        scheduler: APScheduler instance
    """
    global _scheduler
    _scheduler = scheduler


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance.

    Returns:
        AsyncIOScheduler instance or None if not initialized
    """
    return _scheduler
