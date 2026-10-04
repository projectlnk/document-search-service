from app.db.session import engine
from app.db.base import Base
from app.db.elastic import init_elasticsearch
from app.models.document import Document  # noqa: F401


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_elasticsearch()