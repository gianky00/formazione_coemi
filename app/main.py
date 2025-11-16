import uvicorn
import google.generativeai as genai
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import main as api_router
from app.api.routers import tuning as tuning_router
from app.db.session import engine
from app.db.models import Base
from app.core.config import settings
from app.db.seeding import seed_database

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

    yield

    # Shutdown
    # Add any cleanup logic here

app = FastAPI(
    title="Intelleo",
    description="API for the Intelleo desktop application.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(api_router.router, prefix="/api/v1")
app.include_router(tuning_router.router, prefix="/api/v1/tuning", tags=["Tuning"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
