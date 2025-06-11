from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    health,
    context_search,
    context_retrieve,
    stage1,          # ← add this
)

app = FastAPI(title="SourceSherpa API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(context_search.router)
app.include_router(context_retrieve.router)
app.include_router(stage1.router)   # now resolvable