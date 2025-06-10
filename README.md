# 🚀 SourceSherpa

[![CI](https://github.com/scott-london/SourceSherpa/actions/workflows/python-tests.yml/badge.svg)](https://github.com/scott-london/SourceSherpa/actions/workflows/python-tests.yml)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=scott-london_SourceSherpa&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=scott-london_SourceSherpa)
![style=gangster](https://img.shields.io/badge/🔫%20style-gangster-brightgreen)

**_The LLM context wrangler. Modular, multi-stage, and extensible—just like your codebase wishes it was._**

---

> **What does this repo do?**  
> Extracts, stores, and serves _just enough_ source code context for AI agents and RAG—so your LLMs don’t hallucinate your whole architecture.

---

## 💹 Status

- **CI:** [![CI](https://github.com/scott-london/SourceSherpa/actions/workflows/python-tests.yml/badge.svg)](https://github.com/scott-london/SourceSherpa/actions/workflows/python-tests.yml)
- **SonarCloud:** [![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=scott-london_SourceSherpa&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=scott-london_SourceSherpa)
- **Coverage:** _Coming soon!_
- **Auto-dependency updates:** **[Enabled with Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates)**

---

## 🔁 Multi-Stage, Pluggable Storage & Retrieval

**SourceSherpa is designed for _multi-stage codebase question answering_.**

| Stage | Storage     | Handles                                                                                  |
|-------|-------------|------------------------------------------------------------------------------------------|
| 1     | MongoDB     | Broad codebase questions. Table of contents, features, “What’s here?”                    |
| 2     | Qdrant + Embeds | Deep/semantic code questions. Details, code structure, relationships                |
| 3     | Plug your own! | Want Redis? Pinecone? Custom API? Drop it in.                                         |

### 🟢 Example Flow:
1. **“What does this project do?”** → Fast top-level via MongoDB.
2. **“What’s in the device domain?”** → Qdrant vector search.
3. **“Show me validation code.”** → Embeddings or file chunk search.

---

## 🗂️ Project Structure

| Folder           | What it does                                                                                 |
|------------------|---------------------------------------------------------------------------------------------|
| `src/context/`   | Context block schema, “knowledge objects” for storage & retrieval                           |
| `src/extractors/`| Parses codebases & extracts features based on patterns                                      |
| `src/patterns/`  | Language/framework matching patterns (globs, regexes, etc.)                                 |
| `src/storage/`   | Read/write context to MongoDB, Qdrant, or your next plugin                                  |
| `src/api/`       | The MCP (Model Context Protocol) API endpoints for agents & LLMs                            |
| `generated/`     | All generated/temporary files (auto .gitignored)                                            |
| `tests/`         | Tests and fixtures                                                                          |

---

## ⚡️ Code Feature Extraction: How It Works

1. **Load Patterns:** Patterns from Mongo define _what to look for_ (e.g. `*Controller.cs`).
2. **Scan & Categorize:** Each file/AST output is categorized and mapped to a “feature.”
3. **Export:** Everything lands in a flat JSON (see below).
4. **Load to DB:** Use loaders to inject features/patterns into MongoDB (for queries).

**Sample Output (feature block):**

```json
{
  "repo": "project-x",
  "program": "my-solution",
  "group": "Controller",
  "value": "src/Controllers/WidgetController.cs",
  "matched_pattern": "Controllers/*Controller.cs",
  "notes": "Handles widget endpoints",
  "source_file": "WidgetController.cs.json"
}
```

---

## ⚡️ Quickstart

### 1. Clone & Setup

```bash
git clone https://github.com/scott-london/SourceSherpa.git
cd SourceSherpa
python3 -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 2. Start MongoDB (Docker)

```<bash>
cd src
docker compose -f docker-compose.mongo.yml up -d
```
---

### 3. Load Patterns and Features
'''bash
# Load default patterns
python src/storage/pattern_loader.py

# Load your code features (from extraction step)
python src/storage/feature_loader.py --input generated/ast_output/features_and_patterns.json
```
---

### 4. Run Tests

'''bash
pytest tests/storage/ -v
```
---

### 🛡️ Configuration

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

- **MongoDB credentials are not hardcoded**.  
  They are securely injected at runtime using [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

### CI Secrets Setup (Maintainers Only)

1. Go to your repository on GitHub.
2. Click `Settings` > `Secrets and variables` > `Actions`.
3. Click `New repository secret` and add the following:

   | Name               | Example Value      |
   |--------------------|-------------------|
   | MONGODB_USERNAME   | root              |
   | MONGODB_PASSWORD   | [yourpassword]    |
   | MONGODB_DATABASE   | sourcesherpa      |

4. These secrets are **never exposed in logs or code**.

### Local Development

- For local runs, copy `.env.example` to `.env` and fill in the correct values.
- **Never commit real secrets or passwords to the repository.**

> **Note:**  
> CI will fail if required secrets are not set.  
> For more info, see [GitHub Actions: Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

---

## 🧩 How This Fits

- **Input:** AST-extracted or raw code filepaths, plus patterns from Mongo.
- **Process:** Script matches files to roles using glob patterns and heuristics.
- **Output:** JSON array for each code feature.
- **Next step:** Load this into Mongo, serve via your API.

---

## Tree-sitter API Sidecar (AST Parsing)

For robust, language-agnostic AST parsing, SourceSherpa uses a Dockerized tree-sitter API sidecar. This isolates all tree-sitter and grammar build dependencies from your main environment.

### How it works
- A prebuilt `my-languages.so` (tree-sitter grammars) is included in the Docker build context.
- The sidecar exposes a REST API at `/parse` for supported languages (C#, TypeScript, TSX, CSS, HTML, JavaScript, JSON, etc.).
- Your extractors POST source files to this API and receive AST-derived features as JSON.

### Running the Sidecar
1. **Build the Docker image:**
   ```zsh
   # From project root
   cp build/my-languages.so src/docker/tree_sitter_api/
   cd src/docker/tree_sitter_api
   docker build -t treesitter-api .
   ```
2. **Run the container:**
   ```zsh
   docker run --rm -p 9000:9000 treesitter-api
   ```

### Using the API from Python
```python
import requests

def parse_with_treesitter_api(filepath, lang_id, api_url="http://localhost:9000/parse"):
    with open(filepath, "rb") as f:
        files = {"file": (filepath, f)}
        data = {"lang_id": lang_id}
        resp = requests.post(api_url, files=files, data=data)
        resp.raise_for_status()
        return resp.json()["features"]

# Example usage:
features = parse_with_treesitter_api("path/to/your/file.cs", "c_sharp")
print(features)
```
- `lang_id` must match a supported grammar (e.g. `c_sharp`, `typescript`, `tsx`, `css`, `html`, `javascript`, `json`).

Building the .so file is still problematic, this will need to get sorted out at some point.

### Supported Languages
- The grammars included in `my-languages.so` determine which languages are supported. To add or update grammars, rebuild the `.so` file and update the Docker build context.

### Why this approach?
- **No dependency spiral:** No need to install or build tree-sitter locally.
- **Reproducible:** The API is always consistent, regardless of host OS or Python version.
- **Easy CI/CD:** The sidecar can be run in any environment that supports Docker.

---

## 🤘 Made with ❤️ by Scott London (and AI)