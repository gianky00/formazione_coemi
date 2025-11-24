import uvicorn
import google.generativeai as genai
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api import main as api_router
from app.api.routers import notifications as notifications_router
from app.api.routers import auth, users, audit, config, system
from app.db.session import engine
from app.db.models import Base
from app.core.config import settings
from app.core.db_security import db_security
from app.db.seeding import seed_database
from app.services.notification_service import check_and_send_alerts

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    app.state.startup_error = None

    # Initialize DB Security (Load into RAM, Check Lock)
    try:
        db_security.load_memory_db()
        # Note: engine is statically configured in session.py to use db_security.get_connection
    except PermissionError as e:
        print(f"CRITICAL: {e}")
        app.state.startup_error = str(e)
        yield
        return
    except Exception as e:
        print(f"CRITICAL DB ERROR: {e}")
        app.state.startup_error = f"Database Error: {e}"
        yield
        return

    # Startup
    try:
        Base.metadata.create_all(bind=engine)
        seed_database()
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

        # Schedule the daily alert job
        scheduler.add_job(check_and_send_alerts, 'cron', hour=8, minute=0)

        # Schedule DB Sync (Every 5 minutes) to save RAM data back to disk (if locked)
        scheduler.add_job(db_security.sync_db, 'interval', minutes=5)

        scheduler.start()
    except Exception as e:
        print(f"CRITICAL STARTUP ERROR: {e}")
        app.state.startup_error = str(e)

    yield

    # Shutdown
    if not hasattr(app.state, "startup_error") or not app.state.startup_error:
        try:
            scheduler.shutdown()
        except: pass
        # Save and Unlock
        db_security.cleanup()

app = FastAPI(
    title="Intelleo",
    description="API for the Intelleo desktop application.",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def check_startup_error(request: Request, call_next):
    if hasattr(request.app.state, "startup_error") and request.app.state.startup_error:
        return JSONResponse(
            status_code=503,
            content={"detail": request.app.state.startup_error}
        )
    return await call_next(request)

# Include API routers
app.include_router(api_router.router, prefix="/api/v1")
app.include_router(notifications_router.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
