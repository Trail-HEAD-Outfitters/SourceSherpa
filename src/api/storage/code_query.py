"""
Thin wrapper around the Stage-2 vector store (Qdrant).
Only 'fetch' is mandatory for /context/retrieve; 'semantic_search' added for later.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant
from src.config.settings import settings

_COLLECTION = "code"          # Qdrant collection name

class CodeQuery:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)

    # ---------- retrieve by point IDs ------------------
    def fetch(self, ids: List[str]) -> List[Dict[str, Any]]:
        if not ids:
            return []
        points = self.client.get(
            collection_name=_COLLECTION,
            ids=ids,
            with_payload=True,
            with_vectors=False,
        )
        # Flatten and strip internal fields
        return [
            {
                "id": p.id,
                **p.payload,       # repo, value, code, etc.
            }
            for p in points
        ]

    # ---------- semantic search (optional) -------------
    def semantic_search(
        self,
        vector: List[float],
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ):
        flt = (
            qdrant.Filter(
                must=[qdrant.FieldCondition(key=k, match=qdrant.MatchValue(value=v)) for k, v in filters.items()]
            )
            if filters
            else None
        )
        res = self.client.search(
            collection_name=_COLLECTION,
            query_vector=vector,
            limit=k,
            query_filter=flt,
            with_payload=True,
        )
        return [{"id": r.id, "score": r.score, **r.payload} for r in res]