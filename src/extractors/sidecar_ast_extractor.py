"""
Walk SOURCE_IN, POST C#/TS/TSX files to the Tree-sitter sidecar,
write the returned features JSON next to other source blobs.

Sidecar URL read from env TS_API (default http://localhost:9000).
"""

import os, json, requests
from pathlib import Path

ROOT       = Path(__file__).resolve().parents[2]
SOURCE_IN  = ROOT / "repos"                      # adjust as needed
OUT_DIR    = ROOT / "generated" / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TS_API = os.getenv("TS_API", "http://localhost:9000")

LANG_MAP = {
    ".cs"  : "c_sharp",
    ".ts"  : "typescript",
    ".tsx" : "tsx",
    ".css" : "css",
    ".html": "html",
    ".js"  : "javascript",
    ".json": "json",
    # Add more as you add grammars
}

def extract_one(fp: Path):
    ext = fp.suffix.lower()
    if ext in LANG_MAP:
        with fp.open("rb") as f:
            resp = requests.post(
                f"{TS_API}/parse",
                params={"lang_id": LANG_MAP[ext]},
                files={"file": (fp.name, f, "text/plain")},
                timeout=30,
            )
        resp.raise_for_status()
        feats = resp.json()["features"]
    else:
        # plain-text fallback
        feats = [{
            "filepath": str(fp.relative_to(SOURCE_IN)),
            "lang": ext.lstrip("."),
            "source": fp.read_text("utf-8", errors="ignore"),
        }]

    out = OUT_DIR / fp.relative_to(SOURCE_IN)
    out.parent.mkdir(parents=True, exist_ok=True)
    out = out.with_suffix(ext + ".json")
    out.write_text(json.dumps(feats, ensure_ascii=False), encoding="utf-8")

def main():
    files = [p for p in SOURCE_IN.rglob("*") if p.is_file()]
    print(f"Scanning {len(files)} files …")
    for fp in files:
        extract_one(fp)
    print("✅  sidecar_ast_extractor complete.")

if __name__ == "__main__":
    main()
