from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.db.session import get_db
from app.schemas.document import DocumentResponse
from app.services.search_service import search_documents, delete_document_from_index
from app.models.document import Document

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/search", response_model=List[DocumentResponse])
async def search_docs(
    q: str = Query(..., description="Поисковый запрос"),
    db: AsyncSession = Depends(get_db)
):
    # 1. Searching in Elasticsearch, getting list of ID
    doc_ids = await search_documents(query=q, size=20)
    
    if not doc_ids:
        return []

    # 2. Getting documents from PostgreSQL
    stmt = select(Document).where(Document.id.in_(doc_ids))
    result = await db.execute(stmt)
    documents = result.scalars().all()

    # 3. Sorting by creation date
    documents.sort(key=lambda doc: doc.created_date, reverse=True)

    return documents


@router.delete("/{doc_id}", status_code=204)
async def delete_doc(
    doc_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 1. Checking ig existing in database
    stmt = select(Document).where(Document.id == doc_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    # 2. Delete from PostgreSQL
    await db.execute(delete(Document).where(Document.id == doc_id))
    await db.commit()

    # 3. Delete from Elasticsearch
    await delete_document_from_index(doc_id)

    return None