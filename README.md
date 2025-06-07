# SourceSherpa

A modular backend for extracting, storing, and serving source code context for LLM/RAG workflows.

## 🚀 Quickstart

### 1. Clone and Setup Your Virtual Environment

```bash
git clone <your-sourcesherpa-repo-url>
cd sourcesherpa
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

---

### 2 Dev Notes
pip install -e .
uvicorn api.main:app --reload --app-dir src
python src/cli/main.py extract_and_load
curl -X POST "http://127.0.0.1:8000/context/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Where are controllers?", "patterns": ["Controller"], "max_blocks": 5}'

---


## Project Structure

- `src/api` — FastAPI API layer
- `src/storage` — Storage backends (Mongo, etc)
- `src/context` — Context block schema/assembly
- `src/extractors` — Extractor skeletons
- `src/patterns` — Patterns for code matching
- `src/cli` — CLI entrypoint
- `tests/` — Tests, fixture repos

---
# SourceSherpa
