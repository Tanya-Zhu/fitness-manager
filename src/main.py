"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from pathlib import Path

from src.core.config import settings
from src.core.scheduler import set_scheduler, get_scheduler
from src.api.middleware.validation import validation_exception_handler
from src.api.middleware.error_handler import (
    AppException,
    app_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from src.api.routes import health, plans, auth, workout_logs, gym_exercises, plan_execution_routes, plan_member_routes
from src.core.config import settings


app = FastAPI(
    title="运动管家 - 健身计划管理 API",
    description="健身计划创建、管理和提醒功能的 RESTful API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register API routers
app.include_router(health.router)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(plans.router, prefix=settings.api_v1_prefix)
app.include_router(workout_logs.router, prefix=settings.api_v1_prefix)
app.include_router(gym_exercises.router, prefix=settings.api_v1_prefix)
app.include_router(plan_execution_routes.router, prefix=settings.api_v1_prefix)
app.include_router(plan_member_routes.router)

# 挂载静态文件目录（必须在最后，因为包含根路径）
static_path = Path(__file__).parent.parent / "static"
app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    print("🚀 Application starting...")
    print(f"📝 Environment: {settings.app_env}")
    print(f"📖 API Documentation: http://localhost:8000/docs")

    # Initialize APScheduler
    try:
        # Configure job store (Redis or Memory)
        if settings.redis_url.startswith("memory://"):
            # 轻量版：使用内存存储（无需 Redis）
            print("📦 Using memory job store (lightweight mode)")
            scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        else:
            # 完整版：使用 Redis 存储
            jobstores = {
                "default": RedisJobStore(
                    host=settings.redis_url.split("://")[1].split(":")[0],
                    port=int(settings.redis_url.split(":")[-1].split("/")[0]),
                    db=int(settings.redis_url.split("/")[-1]) if "/" in settings.redis_url else 0,
                )
            }
            scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Asia/Shanghai")

        scheduler.start()
        set_scheduler(scheduler)
        print("⏰ APScheduler started successfully")
    except Exception as e:
        print(f"⚠️ Failed to start APScheduler: {e}")
        print("   Scheduler will not be available for reminders")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    print("👋 Application shutting down...")

    # Shutdown APScheduler
    scheduler = get_scheduler()
    if scheduler:
        try:
            scheduler.shutdown(wait=True)
            print("⏰ APScheduler shutdown successfully")
        except Exception as e:
            print(f"⚠️ Error shutting down APScheduler: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )
