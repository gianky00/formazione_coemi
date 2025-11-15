import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import main as api_router
from app.api.routers import tuning as tuning_router
from app.api.main import seed_database
from app.db.models import Base
from app.db.session import engine

import google.generativeai as genai
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router.router)
app.include_router(tuning_router.router, prefix="/api/v1/tuning", tags=["tuning"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
