from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from sourcesherpa.storage.mongo import MongoContextSource

app = FastAPI()

mongo_source = MongoContextSource(uri="mongodb://localhost:27017", db_name="sourcesherpa")

class QueryRequest(BaseModel):
    question: str
    patterns: Optional[List[str]] = None
    max_blocks: int = 10

@app.post("/context/query")
def context_query(req: QueryRequest):
    # Simple: just filter by pattern for now
    mongo_query = {}
    if req.patterns:
        mongo_query["pattern"] = {"$in": req.patterns}
    blocks = mongo_source.find_blocks(mongo_query)[:req.max_blocks]
    return {"context_blocks": blocks}
