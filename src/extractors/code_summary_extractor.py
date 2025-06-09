"""
Table‑of‑Contents (Stage 1) extractor.

Scans the JSON artifacts produced by your AST parser and produces a single
`patterns_and_features.json` that maps every source file to one of the
pattern “buckets” stored in MongoDB.

* **Input  :** <repo‑root>/generated/output/**.json  (unchunked AST output)
* **Output :** <repo‑root>/generated/ast_output/patterns_and_features.json

Run it after **`src/storage/pattern_loader.py`** so that the `patterns`
collection is populated.

Example:
```
python -m src.extractors.toc_extractor --debug
```
"""
from __future__ import annotations

import argparse
import fnmatch
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pymongo import MongoClient
from src.config.settings import settings

# -----------------------------------------------------------------------------
# 📁 Filesystem locations
# -----------------------------------------------------------------------------
ROOT               = Path(__file__).resolve().parents[2]              # repo root
INPUT_DIR          = ROOT / "generated" / "output"                  # AST parser out
OUTPUT_DIR         = ROOT / "generated" / "ast_output"             # Stage‑1 out
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE           = OUTPUT_DIR / "patterns_and_features.json"       # final file

# -----------------------------------------------------------------------------
# 🛢️ MongoDB
# -----------------------------------------------------------------------------
mongo = MongoClient(settings.mongodb_uri)[settings.mongodb_database]
PATTERNS: List[Dict[str, Any]] = list(mongo["patterns"].find({}, {"_id": 0}))

# -----------------------------------------------------------------------------
# 🛠️ Extractor
# -----------------------------------------------------------------------------
class TOCExtractor:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.features: List[Dict[str, Any]] = []
        self._d(f"Loaded {len(PATTERNS)} patterns from MongoDB.")
        if PATTERNS:
            self._d(f"Sample pattern: {PATTERNS[0]}")

    # ------------------------------------------------------------ helpers -----
    def _d(self, msg: str) -> None:
        pass  # Disable all debug output

    @staticmethod
    def _norm(path: str) -> str:
        return path.replace("\\", "/")

    def _repo_program(self, full_path: str) -> tuple[str, str]:
        parts = self._norm(full_path.lower()).split("/")
        if "dev" in parts:
            i = parts.index("dev")
            if len(parts) > i + 2:
                return parts[i + 2], parts[i + 1]  # repo, program
        repo = parts[0] if parts else "unknown"
        return repo, repo.split("-")[0]

    # ------------------------------------------------------------- core ------
    def _match(self, file_path: str, src_file: str) -> None:
        repo, program = self._repo_program(file_path)
        basename      = Path(file_path).name.lower()
        # Strip .json extension if present
        if basename.endswith('.json'):
            basename = basename[:-5]
        matched = False
        for pat in PATTERNS:
            # 1️⃣ filename match
            if not any(fnmatch.fnmatch(basename, g.lower()) for g in pat["file_patterns"]):
                continue
            # 2️⃣ directory constraint (if any)
            if dirs := pat.get("directories"):
                if not any(d.lower() in file_path.lower() for d in dirs):
                    continue
            # ✅ record feature and stop at first hit
            self.features.append({
                "repo": repo,
                "program": program,
                "group": pat["keyword"],
                "value": file_path,
                "matched_pattern": pat["file_patterns"][0],
                "notes": pat.get("notes", ""),
                "source_file": src_file,
            })
            matched = True
            break
        if not matched:
            # Still record the file, but with minimal info and no pattern fields
            self.features.append({
                "repo": repo,
                "program": program,
                "value": file_path,
                "source_file": src_file
            })

    def walk(self) -> None:
        json_files = list(INPUT_DIR.rglob("*.json"))
        self._d(f"Found {len(json_files)} AST JSON files under {INPUT_DIR}.")
        sample_entries = []
        for jf in json_files:
            if not jf.is_file():
                self._d(f"Skipping directory: {jf}")
                continue
            with jf.open(encoding="utf-8") as fp:
                data = json.load(fp)

            entries: List[str] = []
            if isinstance(data, list):
                for e in data:
                    if isinstance(e, str):
                        entries.append(e)
                    elif isinstance(e, dict):
                        if 'filepath' in e:
                            entries.append(e['filepath'])
                        elif 'value' in e:
                            entries.append(e['value'])
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, str):
                        entries.append(v)
                    elif isinstance(v, dict):
                        if 'filepath' in v:
                            entries.append(v['filepath'])
                        elif 'value' in v:
                            entries.append(v['value'])
                    elif isinstance(v, list):
                        for x in v:
                            if isinstance(x, str):
                                entries.append(x)
                            elif isinstance(x, dict):
                                if 'filepath' in x:
                                    entries.append(x['filepath'])
                                elif 'value' in x:
                                    entries.append(x['value'])
            else:
                self._d(f"Unknown data shape in {jf}")
                continue  # skip unknown shapes

            if not entries:
                self._d(f"No string or dict entries found in {jf}")
            for path in entries:
                if len(sample_entries) < 10:
                    sample_entries.append(path)
                self._match(path, jf.name)
        if sample_entries:
            self._d(f"Sample entries: {sample_entries}")

    # ----------------------------------------------------------- output ------
    def save(self) -> None:
        OUT_FILE.write_text(json.dumps(self.features, indent=2), encoding="utf-8")
        print(f"Wrote {len(self.features)} features ➜ {OUT_FILE.relative_to(ROOT)}")
        self.print_duplicates(self.features)

    def print_duplicates(self, features: list[dict]) -> None:
        seen = {}
        dups = []
        for row in features:
            key = (row.get("repo"), row.get("value"), row.get("hash"))
            if key in seen:
                dups.append(row)
            else:
                seen[key] = row
        if dups:
            for dup in dups:
                print(json.dumps(dup, indent=2))
        # Print only duplicates, nothing else

# -----------------------------------------------------------------------------
# 🚀 CLI
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate patterns_and_features.json from AST output.")
    parser.add_argument("--debug", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    ext = TOCExtractor(debug=args.debug)
    ext.walk()
    ext.save()
