import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import main as api_router
from app.api.main import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
