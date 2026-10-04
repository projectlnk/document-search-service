from typing import List, Dict, Any
from app.db.elastic import es_client, DOCUMENTS_INDEX


async def index_document(doc_id: int, text: str) -> None:
    """Indexing document to Elasticsearch."""
    await es_client.index(
        index=DOCUMENTS_INDEX,
        id=doc_id,
        document={"id": doc_id, "text": text},
        refresh=True
    )


async def delete_document_from_index(doc_id: int) -> None:
    await es_client.delete(
        index=DOCUMENTS_INDEX,
        id=doc_id,
        ignore=[404],
        refresh=True
    )


async def search_documents(query: str, size: int = 20) -> List[int]:
    response = await es_client.search(
        index=DOCUMENTS_INDEX,
        query={
            "match": {
                "text": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        },
        size=size
    )
    return [hit["_source"]["id"] for hit in response["hits"]["hits"]]