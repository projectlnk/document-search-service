import pytest
from datetime import datetime, timezone
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.document import Document
from app.services.search_service import index_document


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_search_empty_query(client):
    response = await client.get("/documents/search", params={"q": "уникальноеслово12345"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_and_delete_flow(client):
    unique_word = "тестпроверкафлоу"
    async with async_session_maker() as session:
        doc = Document(
            rubrics=["test"],
            text=f"Это уникальный текст со словом {unique_word}",
            created_date=datetime.now(timezone.utc)
        )
        session.add(doc)
        await session.flush()
        doc_id = doc.id
        await index_document(doc.id, doc.text)
        await session.commit()

    response = await client.get("/documents/search", params={"q": unique_word})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    found_ids = [d["id"] for d in data]
    assert doc_id in found_ids

    delete_response = await client.delete(f"/documents/{doc_id}")
    assert delete_response.status_code == 204

    async with async_session_maker() as session:
        result = await session.execute(select(Document).where(Document.id == doc_id))
        assert result.scalar_one_or_none() is None

    search_after_delete = await client.get("/documents/search", params={"q": unique_word})
    assert search_after_delete.status_code == 200
    assert doc_id not in [d["id"] for d in search_after_delete.json()]


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client):
    response = await client.delete("/documents/999999999")
    assert response.status_code == 404