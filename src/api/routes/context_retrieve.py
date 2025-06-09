from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from src.api.storage.code_query import CodeQuery

router = APIRouter(prefix="/v1/context", tags=["context"])

@router.post("/retrieve")
def retrieve(ids: List[str] = Body(..., embed=True)) -> List[Dict[str, Any]]:
    """
    Given a list of point IDs from Qdrant, return full code chunks ready
    for prompt injection.
    """
    docs = CodeQuery().fetch(ids)
    if not docs:
        raise HTTPException(404, detail="No documents found for given ids")
    return docs