from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional

from src.api.storage.feature_query import FeatureQuery

router = APIRouter(prefix="/v1/context", tags=["context"])

class SearchHit(BaseModel):
    repo: str
    program: str
    group: str
    value: str
    snippet: Optional[str] = None
    lang:   Optional[str] = None
    score:  float

def get_fq() -> FeatureQuery:  # dependency
    return FeatureQuery()

@router.post("/search", response_model=List[SearchHit])
def search_features(
    query: str = Query(..., description="Free-text search"),
    k:     int = Query(10,  ge=1, le=50),
    repo:  Optional[str] = None,
    group: Optional[str] = None,
    program: Optional[str] = None,
    lang:   Optional[str] = None,
    fq: FeatureQuery = Depends(get_fq),
):
    """Stage-1 TOC search (Mongo)."""
    return fq.search(
        query, k=k, repo=repo, program=program, group=group, lang=lang
    )