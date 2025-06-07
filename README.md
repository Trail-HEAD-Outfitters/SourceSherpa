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
📦 Project Structure & Responsibilities

This repo is organized so you can extract, store, and serve code context blocks for LLMs and agent workflows—modularly and language-agnostically.

Folder Breakdown
	•	src/context/
Defines the schema and handling for “context blocks”—the core unit of knowledge exchanged and stored.
Contains the ContextBlock class for code features, file snippets, and metadata.
	•	src/extractors/
Logic for parsing codebases and extracting features.
Extractors use patterns to find relevant files or code elements (e.g., controllers, services), and create ContextBlocks.
	•	src/patterns/
Reusable language/framework-specific matching patterns.
For example: “find all *Controller.cs files in a .NET repo,” or “look for React components.”
Patterns are used by extractors to guide what to pull out of codebases.
	•	src/storage/
Handles reading/writing context blocks to persistent storage.
Supports different backends (MongoDB, Qdrant, etc.) so you can plug in whatever’s best for your retrieval needs.
	•	src/api/
Implements the MCP (Model Context Protocol): the API endpoint that agents and LLMs call to get context blocks.
When an agent asks a question, the API queries storage/ for matching blocks and returns them in the format defined by context/.