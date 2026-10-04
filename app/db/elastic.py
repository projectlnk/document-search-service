import asyncio
import logging
from elasticsearch import AsyncElasticsearch
from app.core.config import settings

logger = logging.getLogger(__name__)

es_client = AsyncElasticsearch(
    hosts=[f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"]
)

DOCUMENTS_INDEX = "documents"


async def init_elasticsearch(retries: int = 10, delay: float = 3.0):
    """
    Create documents index, if doesn't exist.
    С retry — for case is ElasticSearch doesn't ready.
    """
    for attempt in range(1, retries + 1):
        try:
            if not await es_client.indices.exists(index=DOCUMENTS_INDEX):
                await es_client.indices.create(
                    index=DOCUMENTS_INDEX,
                    mappings={
                        "properties": {
                            "id": {"type": "integer"},
                            "text": {"type": "text"},
                        }
                    },
                )
                logger.info(f"✅ Index '{DOCUMENTS_INDEX}' created")
            else:
                logger.info(f"ℹ️ Index '{DOCUMENTS_INDEX}' is already exist")
            return
        except Exception as e:
            logger.warning(
                f"Attempt {attempt}/{retries} connection to Elasticsearch failed: {e}"
            )
            if attempt == retries:
                logger.error("Elasticsearch connection failed")
                raise
            await asyncio.sleep(delay)


async def close_elasticsearch():
    await es_client.close()