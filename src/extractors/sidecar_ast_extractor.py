#!/usr/bin/env python3
"""
Refactored Tree-sitter Sidecar AST Extractor

- Walks SOURCE_IN tree, posts eligible files to the TS_API sidecar
- Emits raw AST JSON for each file under OUT_DIR preserving directory structure
- Includes robust logging, error handling, concurrency, and filetype mapping

Usage:
    python src/extractors/sidecar_ast_extractor.py --source pyxis --out generated/ast_output/output
"""
import os
import json
import argparse
import requests
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s"
)
logger = logging.getLogger(__name__)

# Supported languages mapping
LANG_MAP = {
    ".cs":  "c_sharp",
    ".ts":  "typescript",
    ".tsx": "tsx",
    ".js":  "javascript",
    ".css": "css",
    ".html":"html",
    ".json":"json",
}

# Fallback MIME type
FALLBACK_MIME = "text/plain"


def extract_file(fp: Path, source_root: Path, out_root: Path, ts_api: str) -> None:
    """
    Send a file to Tree-sitter sidecar and write out AST JSON.
    """
    try:
        rel = fp.relative_to(source_root)
        ext = fp.suffix.lower()
        if ext in LANG_MAP:
            lang_id = LANG_MAP[ext]
            with fp.open("rb") as f:
                resp = requests.post(
                    f"{ts_api}/parse",
                    params={"lang_id": lang_id},
                    files={"file": (fp.name, f, FALLBACK_MIME)},
                    timeout=30,
                )
            resp.raise_for_status()
            feats = resp.json().get("features", [])
        else:
            # Fallback for unsupported extensions
            text = fp.read_text("utf-8", errors="ignore")
            feats = [{
                "filepath": str(rel),
                "lang": ext.lstrip('.'),
                "source": text,
            }]
        # Write output
        out_path = out_root / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_file = out_path.with_suffix(ext + ".json")
        out_file.write_text(json.dumps(feats, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.debug(f"Extracted AST for {rel} → {out_file.relative_to(out_root)}")
    except Exception as e:
        logger.error(f"Failed to extract {fp}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sidecar AST Extractor")
    parser.add_argument(
        "--source", "-s", type=Path, required=True,
        help="Root directory of source files to parse"
    )
    parser.add_argument(
        "--out", "-o", type=Path, required=True,
        help="Output directory for AST JSON"
    )
    parser.add_argument(
        "--ts-api", type=str, default=os.getenv("TS_API", "http://localhost:9000"),
        help="Tree-sitter sidecar API endpoint"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=8,
        help="Number of parallel workers"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Delete output directory before extracting"
    )
    args = parser.parse_args()

    source_root = args.source.resolve()
    out_root = args.out.resolve()
    ts_api = args.ts_api.rstrip('/')

    if not source_root.is_dir():
        logger.error(f"Source directory not found: {source_root}")
        return

    if args.clean and out_root.exists():
        import shutil
        shutil.rmtree(out_root)
        logger.info(f"Deleted output directory: {out_root}")

    out_root.mkdir(parents=True, exist_ok=True)
    logger.info(f"Scanning source: {source_root}")

    files = [p for p in source_root.rglob("*") if p.is_file()]
    logger.info(f"Found {len(files)} files to process.")

    # Parallel extraction
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(extract_file, fp, source_root, out_root, ts_api) for fp in files]
        for _ in as_completed(futures):
            pass  # errors logged in extract_file

    logger.info("✅ Sidecar AST extraction complete.")


if __name__ == "__main__":
    main()
