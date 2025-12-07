import uvicorn
import google.generativeai as genai
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api import main as api_router
from app.api.routers import notifications as notifications_router
from app.api.routers import auth, users, audit, config, system, app_config, stats, chat
from app.db.session import engine
from app.db.models import Base
from app.core.config import settings
from app.core.db_security import db_security
from app.db.seeding import seed_database
from app.services.notification_service import check_and_send_alerts
from app.services.file_maintenance import organize_expired_files
from app.db.session import SessionLocal
from app.utils.logging import setup_logging
from datetime import datetime, timedelta
from app import __version__
import logging
import sentry_sdk
import os
import sys

# --- SENTRY INTEGRATION ---
if not sentry_sdk.is_initialized():
    environment = "production" if getattr(sys, 'frozen', False) else "development"
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "https://f252d598aaf7e70fe94d533474b76639@o4510490492600320.ingest.de.sentry.io/4510490526744656")

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=environment,
        traces_sample_rate=1.0,
        send_default_pii=True
    )

# Configure logger
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def run_maintenance_task():
    """Background task for file maintenance."""
    try:
        # We don't acquire the global session lock because this task is read-only on DB
        # and filesystem operations are safe enough.
        print("Starting background file maintenance...")
        db = SessionLocal()
        try:
            organize_expired_files(db)
        finally:
            db.close()
        print("Background file maintenance completed.")
    except Exception as e:
        print(f"Error during background file maintenance: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
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
        # We Log but DO NOT BLOCK startup.
        # This allows the UI to launch and prompt the user to fix the DB.
        print(f"WARNING: Database Load Error (Non-Fatal for UI): {e}")
        # We do NOT set app.state.startup_error here to allow Login UI to load.

    # Startup
    try:
        # Attempt to create tables and seed.
        # If this fails (e.g. corrupted DB), we catch it and continue so the UI can handle recovery.
        try:
            Base.metadata.create_all(bind=engine)
            seed_database()
        except Exception as e:
            logger.warning(f"Database Seeding/Migration failed: {e}. Proceeding in Recovery Mode.")
            # Do NOT raise. Continue.

        # EXPLICITLY REMOVED AUTO-CREATION logic per user request.
        # The database file is created only via the "Create New Database" UI flow in launcher.py.
        if not db_security.db_path.exists():
            logger.warning(f"Database file not found at {db_security.db_path}. Waiting for UI recovery.")

        # File Maintenance is now deferred to background task triggered by UI
        # to prevent blocking startup.

        if settings.GEMINI_API_KEY_ANALYSIS:
            genai.configure(api_key=settings.GEMINI_API_KEY_ANALYSIS)

        # Schedule the daily alert job
        scheduler.add_job(check_and_send_alerts, 'cron', hour=8, minute=0)

        # Schedule DB Sync (Every 5 minutes) to save RAM data back to disk (if locked)
        scheduler.add_job(db_security.sync_db, 'interval', minutes=5)

        scheduler.start()
    except Exception as e:
        print(f"STARTUP EXCEPTION (Handled): {e}")
        # Only set startup_error for truly fatal things that prevent the API from even serving status
        # For DB issues, we prefer to let the UI handle it.

    yield

    # Shutdown
    if not hasattr(app.state, "startup_error") or not app.state.startup_error:
        try:
            scheduler.shutdown()
        except Exception as e:
            logger.warning(f"Error during scheduler shutdown: {e}")
        # Save and Unlock
        db_security.cleanup()

app = FastAPI(
    title="Intelleo",
    description="API for the Intelleo desktop application.",
    version=__version__,
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

@app.get("/api/v1/health", tags=["Health"])
async def health_check(request: Request):
    """
    Simple health check endpoint.
    """
    if hasattr(request.app.state, "startup_error") and request.app.state.startup_error:
         return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": request.app.state.startup_error}
        )
    return {"status": "ok"}

# Include API routers
app.include_router(api_router.router, prefix="/api/v1")
app.include_router(notifications_router.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(app_config.router, prefix="/api/v1/app_config", tags=["App Config"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Statistics"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
