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
class SummaryExtractor:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.features: List[Dict[str, Any]] = []
        self._d(f"Loaded {len(PATTERNS)} patterns from MongoDB.")
        if PATTERNS:
            self._d(f"Sample pattern: {PATTERNS[0]}")

    def _d(self, msg: str) -> None:
        if self.debug:
            print(msg)

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

    def extract_entries(self, data: Any) -> List[str]:
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
        return entries

    def find_pattern(self, file_path: str) -> Dict[str, Any] | None:
        basename = Path(file_path).name.lower()
        if basename.endswith('.json'):
            basename = basename[:-5]
        for pat in PATTERNS:
            if not any(fnmatch.fnmatch(basename, g.lower()) for g in pat["file_patterns"]):
                continue
            if dirs := pat.get("directories"):
                if not any(d.lower() in file_path.lower() for d in dirs):
                    continue
            return pat
        return None

    def create_feature(self, file_path: str, src_file: str, pat: Dict[str, Any] | None, repo: str, program: str) -> Dict[str, Any]:
        if pat:
            return {
                "repo": repo,
                "program": program,
                "group": pat["keyword"],
                "value": file_path,
                "matched_pattern": pat["file_patterns"][0],
                "notes": pat.get("notes", ""),
                "source_file": src_file,
            }
        else:
            return {
                "repo": repo,
                "program": program,
                "value": file_path,
                "source_file": src_file
            }

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
            entries = self.extract_entries(data)
            if not entries:
                self._d(f"No string or dict entries found in {jf}")
            for path in entries:
                if len(sample_entries) < 10:
                    sample_entries.append(path)
                repo, program = self._repo_program(path)
                pat = self.find_pattern(path)
                feature = self.create_feature(path, jf.name, pat, repo, program)
                self.features.append(feature)
        if sample_entries:
            self._d(f"Sample entries: {sample_entries}")

    def save(self) -> None:
        OUT_FILE.write_text(json.dumps(self.features, indent=2), encoding="utf-8")
        try:
            rel_path = OUT_FILE.relative_to(ROOT)
        except ValueError:
            rel_path = OUT_FILE
        print(f"Wrote {len(self.features)} features ➜ {rel_path}")
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

    ext = SummaryExtractor(debug=args.debug)
    ext.walk()
    ext.save()
