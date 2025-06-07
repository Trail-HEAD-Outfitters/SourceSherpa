# SourceSherpa

A modular backend for extracting, storing, and serving source code context for LLM/RAG workflows.

## Quickstart

1. Install dependencies:
    pip install -e .

2. Run the API:
    uvicorn sourcesherpa.api.main:app --reload

3. Use the CLI:
    python -m sourcesherpa.cli.main --help

## Project Structure

- `src/sourcesherpa/api` — FastAPI API layer
- `src/sourcesherpa/storage` — Storage backends (Mongo, etc)
- `src/sourcesherpa/context` — Context block schema/assembly
- `src/sourcesherpa/extractors` — Extractor skeletons
- `src/sourcesherpa/patterns` — Patterns for code matching
- `src/sourcesherpa/cli` — CLI entrypoint
- `tests/` — Tests, fixture repos

---
# SourceSherpa
