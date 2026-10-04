from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.init_db import init_db
from app.db.elastic import close_elasticsearch
from app.db.session import engine
from app.api.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_elasticsearch()
    await engine.dispose()


app = FastAPI(
    title="Document Search Service",
    description="Test task for Junior Python Backend Developer",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}