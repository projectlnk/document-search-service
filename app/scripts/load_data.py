import asyncio
import csv
import ast
from datetime import datetime

from app.db.session import async_session_maker, engine
from app.db.init_db import init_db
from app.db.elastic import close_elasticsearch
from app.models.document import Document
from app.services.search_service import index_document

BATCH_SIZE = 1000


async def load_csv(filepath: str = "posts.csv"):
    try:
        await init_db()
        print("Tables and indexes are ready")

        async with async_session_maker() as session:
            with open(filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    try:
                        rubrics_list = ast.literal_eval(row["rubrics"])
                    except (ValueError, SyntaxError):
                        rubrics_list = []

                    try:
                        created_date = datetime.strptime(
                            row["created_date"], "%Y-%m-%d %H:%M:%S"
                        )
                    except ValueError:
                        print(f"Missing string with date: {row['created_date']}")
                        continue

                    doc = Document(
                        rubrics=rubrics_list,
                        text=row["text"],
                        created_date=created_date,
                    )
                    session.add(doc)
                    await session.flush()
                    await index_document(doc.id, doc.text)

                    count += 1
                    if count % BATCH_SIZE == 0:
                        await session.commit()
                        print(f"Loaded {count} documents...")

                await session.commit()
                print(f"Loading is complete! Count of documents: {count}")
    finally:
        await close_elasticsearch()
        await engine.dispose()
        print("Connections closed")


if __name__ == "__main__":
    asyncio.run(load_csv())