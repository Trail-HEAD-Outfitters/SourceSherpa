from typing import List, Dict, Any, Optional
from pymongo import MongoClient, ASCENDING, TEXT
from src.config.settings import settings

class FeatureQuery:
    """Read-only facade over the Stage-1 TOC (Mongo)."""

    def __init__(self, test_mode: bool = False) -> None:
        client = MongoClient(settings.mongodb_uri)
        db     = client[settings.mongodb_database]
        name   = "features_test" if test_mode else "features"
        self.col = db[name]
        self._ensure_indexes()

    # ------------- indexes -----------------------------
    def _ensure_indexes(self) -> None:
        ix = [i["name"] for i in self.col.list_indexes()]
        if "text_all" not in ix:
            self.col.create_index(
                [("value", TEXT), ("snippet", TEXT), ("group", TEXT)],
                name="text_all",
                default_language="english",
            )
        if "meta_uniq" not in ix:
            self.col.create_index(
                [("repo", ASCENDING), ("value", ASCENDING), ("hash", ASCENDING)],
                unique=True,
                name="meta_uniq",
            )

    # ------------- API ---------------------------------
    def search(
        self,
        query: str,
        k: int = 10,
        *,
        repo: Optional[str] = None,
        program: Optional[str] = None,
        group: Optional[str] = None,
        lang: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Full-text + metadata filter search."""
        filt: Dict[str, Any] = {}
        if repo:    filt["repo"]    = repo
        if program: filt["program"] = program
        if group:   filt["group"]   = group
        if lang:    filt["lang"]    = lang

        cursor = (
            self.col.find(
                {"$text": {"$search": query}, **filt},
                {"score": {"$meta": "textScore"}, "_id": 0},
            )
            .sort([("score", {"$meta": "textScore"})])
            .limit(k)
        )
        return list(cursor)