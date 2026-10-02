from pydantic import BaseModel
from typing import Optional


class SearchResponse(BaseModel):
    status: str
    module: str
    count: int
    results: list