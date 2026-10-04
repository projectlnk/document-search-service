from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rubrics: List[str]
    text: str
    created_date: datetime