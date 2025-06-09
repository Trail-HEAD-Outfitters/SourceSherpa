# 🚀 SourceSherpa – The LLM Context Wrangler  
*Multi-stage · Modular · Extensible — like your codebase wishes it was.*

[![CI](https://github.com/<your-org>/SourceSherpa/actions/workflows/python-tests.yml/badge.svg)](https://github.com/<your-org>/SourceSherpa/actions/workflows/python-tests.yml)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=<your-org>_SourceSherpa&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=<your-org>_SourceSherpa)
![style=gangster](https://img.shields.io/badge/🔫%20style-gangster-brightgreen)

> **What is it?**  
> SourceSherpa extracts, stores, and serves *just enough* source-code context to let LLMs answer deep engineering questions **without** hallucinating your whole architecture.  
> Think of it as a RAG-ready, multi-stage “table of contents + vector store” for .NET monoliths, React front-ends, SQL scripts, and everything in between.

---

## 🌐 Why You Might Care

| You need to…                                    | SourceSherpa gives you…                             |
|-------------------------------------------------|-----------------------------------------------------|
| Reverse-engineer features & API surfaces        | A **feature-tagged index** of every Controller / Service / etc. |
| Trace bugs & production exceptions              | **Fine-grained code chunks** retrievable by error, symbol, or embedding |
| Feed an agent / Copilot-style LLM               | A **two-stage retrieval API** that respects context limits |
| Swap models & vector DBs at will                | **Pluggable storage / embedding back-ends** (MongoDB ➜ Qdrant ➜ _You-name-it_) |

---

## 🏗️  Multi-Stage Retrieval Pipeline

```text
                ┌──────────────┐  nightly/CI   ┌───────────────┐
Repos  ───────► │  Extractor   │──────────────►│ Feature Mongo │  (coarse)
(.cs .tsx .sql) └──────────────┘               └───────────────┘
        │  AST + glob                                    ▲
        │  chunk + embed                                 │ metadata
        ▼                                                │
┌───────────────────┐  vectors     ┌──────────────┐      │
│  Embed Service    │────────────►│  Vector DB    │◄─────┘
└───────────────────┘ (BGE / GTE) │  (Qdrant)     │
                                  └──────────────┘
                                         ▲  hybrid search
                                         │
                             ┌───────────┴───────────┐
                             │  Query API / Agent    │
                             │  (AWS Bedrock LLM)    │
                             └───────────┬───────────┘
                                         │
                               Structured Answer JSON
```

| Stage | Store | Purpose | Default Tech |
|-------|-------|---------|--------------|
| **1** | MongoDB | “Table-of-Contents” · fast filters (`Controllers`, `DbContext`, etc.) | `docker-compose.mongo.yml` |
| **2** | Qdrant | Code chunks (~1 k tks) + embeddings · hybrid search (vector + BM25) | `docker-compose.qdrant.yml` |
| **3** | Agent / LLM | Tool-calls: `search_features`, `search_code` · decides when to dive deeper | AWS Bedrock (Claude 3 Sonnet / Titan) |

---

## 🗂️  Repo Layout

| Folder | Purpose |
|--------|---------|
| `src/extractors/`  | Parse C# (Roslyn), TS/React (Tree-sitter), SQL, etc. |
| `src/patterns/`    | Language / framework glob & regex patterns |
| `src/storage/`     | `mongo.py`, `feature_loader.py`, `vec_loader.py` |
| `src/context/`     | Pydantic models for **FeatureBlock** & **CodeChunk** |
| `src/api/`         | FastAPI endpoints + LangChain agent |
| `tests/`           | Unit / integration + fixtures |
| `generated/`       | AST dumps & JSON output (git-ignored) |

---

## ⚡ Quick Start (5 min)

```bash
git clone https://github.com/<your-org>/SourceSherpa.git
cd SourceSherpa
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 1 · Spin up storage

```bash
docker compose -f src/docker-compose.mongo.yml up -d        # MongoDB (TOC)
docker compose -f src/docker-compose.qdrant.yml up -d       # Qdrant (vectors)
```

### 2 · Extract & load one repo

```bash
# Extract features & code chunks
python src/cli/run_extract.py --repo /path/to/your/solution.sln                               --out generated/myrepo_features.json

# Load Stage-1 (Mongo) and Stage-2 (Qdrant)
python src/storage/feature_loader.py  generated/myrepo_features.json
python src/storage/vec_loader.py      generated/myrepo_features.json
```

### 3 · Ask a question

```bash
uvicorn src.api.app:app --reload
# POST /ask  { "question": "Where is the RemoteFacilityController implemented?" }
```

---

## 🔧 Configuration

Create `.env` (copy from `.env.example`) and set:

```dotenv
MONGO_URL=mongodb://root:password@localhost:27017/
QDRANT_URL=http://localhost:6333
EMBED_MODEL=bge-large-en          # BGE, GTE, MiniLM, etc.
LLM_PROVIDER=bedrock_claude3      # or openai_gpt4o, etc.
MAX_CONTEXT_TOKENS=8192
```

All configs are loaded via [`src/config/settings.py`](src/config).

---

## 🛣  MVP Roadmap

1. **Extractor MVP** ✔ (patterns + AST dump → JSON)  
2. **Embedding Loader** ⬜ (chunk → BGE vector → Qdrant)  
3. **Coarse Query API** ⬜ (`/ask` hits Mongo only)  
4. **Agent Router** ⬜ (LLM chooses `search_code` when needed)  
5. **Evaluation Dashboards** ⬜ (precision, latency, token cost)  
6. **Security & PII Guardrails** ⬜ (secret-scrub, repo ACL)  
7. **Docs & Demo notebooks** ⬜

---

## 🧠  How Feature Extraction Works

1. **Load pattern map** (see [`src/patterns/default_patterns.py`](src/patterns)).  
2. **Walk repo**: glob + AST to tag each file with `group`, `lang`, etc.  
3. **Auto-summary**: grab first XML doc-comment or generate one-liner via local LLM.  
4. **Emit `FeatureBlock` JSON**:

```json
{
  "repo": "phg-server",
  "group": "Controller",
  "value": "src/Controllers/RemoteFacilityController.cs",
  "snippet": "Handles CRUD for remote facility records.",
  "lang": "cs",
  "tokens": 845,
  "hash": "53da…a1c9"
}
```

5. **Optional**: dedupe via `(repo, hash)` and skip re-embedding unchanged files.

---

## 🪄  Agent & LLM (Stage 3)

- **Tool schema**:  
  - `search_features(query, k, filters)` → Mongo  
  - `search_code(query, k, filters)`    → Qdrant  
- **Policy**:  
  1. Always call **`search_features`** first.  
  2. If similarity < `CONFIDENCE_THRESHOLD` or answer still unclear → call **`search_code`**.  
  3. Compose final answer with citations (path + line numbers).  
- Implemented with **LangChain**; runs on **AWS Bedrock** (Claude 3 Sonnet, 32 k ctx).  
- Guardrails: max 2 tool calls; if still unsure → ask user for clarification.

---

## 🔐  Secrets & CI

- Secrets injected via **GitHub Actions Encrypted Secrets**.  
- `.env` keeps local credentials; **never check real secrets** into VCS.  
- CI runs lint, tests, SonarCloud scan on every PR.

---

## 🤝  Contributing

PRs & issues welcomed—especially new extraction patterns (.proto, Rust, etc.).  
Run `pre-commit install` to auto-format with Black & Ruff.

---

## 📜  License

MIT © 2024 Scott London & Contributors
