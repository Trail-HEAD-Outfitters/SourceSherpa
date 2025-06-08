# SourceSherpa
## Status
![CI](https://github.com/scott-london/SourceSherpa/actions/workflows/python-tests.yml/badge.svg)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=scott-london_SourceSherpa&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=scott-london_SourceSherpa)

A modular backend for extracting, storing, and serving source code context for LLM/RAG workflows.

### 🗄️ Multi-Stage, Pluggable Storage & Retrieval

SourceSherpa supports **multi-stage question answering**, where each stage of the workflow can use the most appropriate storage or retrieval mechanism for the task.

#### **Stage 1: Top-Level Feature Index (MongoDB)**
- Provides a "table of contents" for the codebase.
- Powers broad, project-level questions:
  - "What kinds of files/features/domains exist?"
  - "How many web pages/controllers/services are there?"
- Data is indexed as feature blocks, stored in MongoDB for fast, flexible lookups.

#### **Stage 2: Semantic & Deep Code Retrieval (Qdrant + Embeddings)**
- Handles detailed, code-specific queries:
  - "What are all the fields in the Device domain?"
  - "How is authentication handled across projects?"
- Uses Qdrant as a vector store, enabling semantic/code similarity via embeddings (e.g., CodeBERT, MiniLM).

#### **Design Pattern: Pluggable Storage Modules**
- Each backend (Mongo, Qdrant, others) is a self-contained module under `src/storage/`.
- The API (MCP) layer routes queries to one or more storage backends depending on the question's stage and specificity.
- Supports easy expansion: add new storage or retrieval mechanisms without breaking the workflow.

#### **Example Flow**
1. **Initial question:** "What does this project do?"
   - Answered using features index in Mongo.
2. **Follow-up:** "Tell me more about the device domain."
   - Answered using semantic search from Qdrant.
3. **Deeper query:** "Show me methods for device validation."
   - Answered via additional indexing, code embeddings, or chunk-level search.

---

**This modular, stage-aware design supports broad discovery, detailed exploration, and future extensibility as your code and data needs grow.**

---
# SourceSherpa
📦 Project Structure & Responsibilities

This repo is organized so you can extract, store, and serve code context blocks for LLMs and agent workflows—modularly and language-agnostically.

Folder Breakdown
	•	src/context/
Defines the schema and handling for "context blocks"—the core unit of knowledge exchanged and stored.
Contains the ContextBlock class for code features, file snippets, and metadata.
	•	src/extractors/
Logic for parsing codebases and extracting features.
Extractors use patterns to find relevant files or code elements (e.g., controllers, services), and create ContextBlocks.
	•	src/patterns/
Reusable language/framework-specific matching patterns.
For example: "find all *Controller.cs files in a .NET repo," or "look for React components."
Patterns are used by extractors to guide what to pull out of codebases.
	•	src/storage/
Handles reading/writing context blocks to persistent storage.
Supports different backends (MongoDB, Qdrant, etc.) so you can plug in whatever's best for your retrieval needs.
	•	src/api/
Implements the MCP (Model Context Protocol): the API endpoint that agents and LLMs call to get context blocks.
When an agent asks a question, the API queries storage/ for matching blocks and returns them in the format defined by context/.



### Extractors
---
### 🛠 Code Feature Extraction Workflow

This module extracts and categorizes source code files using project-specific patterns. It creates a single canonical JSON output (example: `features_and_patterns.json`) that maps code files to their detected roles (controllers, services, models, etc.), ready for use in retrieval-augmented generation (RAG) or agent workflows.

#### **How it works:**
1. **Pattern Loading**:  
   Reads code patterns from the patterns collection in MongoDB (e.g., globs like `Controllers/*Controller.cs`).
2. **File Scanning**:  
   Scans the output directory for code files or AST outputs from multiple repositories.
3. **Categorization**:  
   Matches each file to patterns and assigns a role/group (e.g., "Controller", "Validator", "Service").
4. **Output**:  
   Writes a flattened JSON array, with each entry containing:
   - `repo`: Repository name
   - `program`: Program/grouping identifier
   - `group`: Role/category (from matched pattern)
   - `value`: Path to the code file
   - `matched_pattern`: Which glob/pattern matched
   - `notes`: Free-text notes about the group
   - `source_file`: Originating file (if coming from AST)

**Example output:**

```json
{ 
  "repo": "repo name",
  "program": "broader solution",
  "group": "Controller",
  "value": "/path/to/Controllers/UserController.cs",
  "matched_pattern": "Controllers/*Controller.cs",
  "notes": "ASP.NET MVC & Web-API controllers",
  "source_file": "UserController.cs.json"
}

---

## 🧩 **How This Fits**

- **Input:** AST-extracted or raw code filepaths, plus patterns from Mongo.
- **Process:** Script matches files to roles using glob patterns and heuristics.
- **Output:** JSON array (like [your uploaded file](sandbox:/mnt/data/features_and_patterns.json?_chatgptios_conversationID=684452c5-ee44-800f-8a46-4efb49dd4eeb&_chatgptios_messageID=4af3ee18-6f28-42f9-b5e7-3b55537cfb22)) for each code feature.
- **Next step:** Load this into Mongo, serve via your API.

### 📁 Generated Content

All intermediate outputs and artifacts (AST files, feature lists, etc.) are written to the `generated/` directory at the repo root.

This directory is git-ignored by default (`generated/` in `.gitignore`).

**Example feature loader usage:**
```bash
python src/storage/feature_loader.py --input generated/ast_output/features_and_patterns.json

---

### 🔄 Loading Patterns and Features

To load or refresh patterns (for file categorization):

```bash
python src/storage/pattern_loader.py


## Project Structure

- `src/api` — FastAPI API layer
- `src/storage` — Storage backends (Mongo, etc)
- `src/context` — Context block schema/assembly
- `src/extractors` — Extractor skeletons
- `src/patterns` — Patterns for code matching
- `src/cli` — CLI entrypoint
- `tests/` — Tests, fixture repos


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

## Configuration

This project uses environment variables for configuration. To set up:

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_secure_password
MONGODB_DATABASE=sourcesherpa
```

3. Make sure `.env` is in your `.gitignore` to prevent committing sensitive information.

---
## ⚙️ Continuous Integration & Secrets

This project uses **GitHub Actions** for automated CI testing.

**MongoDB credentials are not hardcoded**.  
They are securely injected at runtime using [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

### CI Secrets Setup (Maintainers Only)

1. **Go to your repository on GitHub.**
2. Click `Settings` > `Secrets and variables` > `Actions`.
3. Click `New repository secret` and add the following:

   | Name               | Example Value    |
   |--------------------|-----------------|
   | MONGODB_USERNAME   | root            |
   | MONGODB_PASSWORD   | [yourpassword ] |
   | MONGODB_DATABASE   | sourcesherpa    |

4. These secrets are **never exposed in logs or code**.

### Local Development

- For local runs, copy `.env.example` to `.env` and fill in the correct values.
- **Never commit real secrets or passwords to the repository.**

---

> **Note:**  
> CI will fail if required secrets are not set.  
> For more info, see [GitHub Actions: Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

