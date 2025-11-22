import uvicorn
import google.generativeai as genai
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api import main as api_router
from app.api.routers import notifications as notifications_router
from app.api.routers import auth, users, audit
from app.db.session import engine
from app.db.models import Base
from app.core.config import settings
from app.db.seeding import seed_database
from app.services.notification_service import check_and_send_alerts

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    Base.metadata.create_all(bind=engine)
    seed_database()
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)

    # Schedule the daily alert job
    scheduler.add_job(check_and_send_alerts, 'cron', hour=8, minute=0)
    scheduler.start()

    yield

    # Shutdown
    scheduler.shutdown()
    # Add any cleanup logic here

app = FastAPI(
    title="Intelleo",
    description="API for the Intelleo desktop application.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(api_router.router, prefix="/api/v1")
app.include_router(notifications_router.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
