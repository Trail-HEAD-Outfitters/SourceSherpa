import os
import json
import hashlib
import logging
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm

# ───── Configuration ─────
load_dotenv(dotenv_path=Path('src/.env.qdrant'))
QDRANT_API_KEY = os.getenv('QDRANT__SERVICE__API_KEY', None)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "raw-ast")
DATA_DIR = Path(os.getenv("AST_DATA_DIR", "generated/ast_output/output"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))

INCLUDE_SUFFIXES = (".json",)  # Only index files ending with .json

# --- File Filtering and Tagging Utilities ---
INCLUDE_EXTS = {".cs", ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".cpp", ".c", ".h", ".html", ".css"}
EXCLUDE_DIRS = {"dist", "build", "obj", "bin", "node_modules", "coverage", "test-results", "__pycache__", ".git"}
EXCLUDE_FILES = {"readme.md", "license", ".gitignore", ".gitattributes", ".env"}

def should_include(path: Path):
    # Only index files that:
    #   - Are .json
    #   - Are NOT in excluded directories
    #   - Are NOT known junk files
    #   - Are for a source file with a valid extension, as inferred by .features.json AST content
    for part in path.parts:
        if part in EXCLUDE_DIRS or part.startswith('.'):
            return False
    if path.name.lower() in EXCLUDE_FILES:
        return False
    return True

def tag_kind(path: Path):
    if path.suffix.lower() == ".json":
        return "source"
    if any(part in {"test", "tests"} for part in path.parts):
        return "test"
    if path.suffix.lower() in INCLUDE_EXTS:
        return "source"
    if path.suffix.lower() in {".md", ".rst"}:
        return "doc"
    if path.suffix.lower() in {".yml", ".yaml"}:
        return "config"
    if path.suffix.lower() in {".exe", ".dll", ".so", ".bin"}:
        return "artifact"
    return "unknown"

# ───── Logging ─────
logging.basicConfig(
    filename='qdrant_loader.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# ───── Device Selection ─────
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
print(f"Using device for embedding: {device}")

# ───── Model Loading ─────
tok = AutoTokenizer.from_pretrained("microsoft/codebert-base")
mdl = AutoModel.from_pretrained("microsoft/codebert-base").to(device)
mdl.eval()

# ───── Chunking Helper ─────
def sliding_windows_tokenizer(text, max_tokens=512, stride=256):
    input_ids = tok(text, return_tensors="pt", truncation=False)["input_ids"][0]
    input_len = len(input_ids)
    for i in range(0, input_len, stride):
        window = input_ids[i : i + max_tokens]
        if window.shape[0] == 0:
            continue
        yield window
        if i + max_tokens >= input_len:
            break

# ───── Embedding Helper ─────
def embed_code_batch(token_windows):
    # Pad to max length in batch
    input_ids = torch.nn.utils.rnn.pad_sequence(token_windows, batch_first=True, padding_value=tok.pad_token_id)
    input_ids = input_ids[:, :512]  # Truncate to 512 tokens
    inputs = {"input_ids": input_ids.to(device)}
    with torch.no_grad():
        outputs = mdl(**inputs)
    arr = outputs.last_hidden_state[:, 0, :].cpu()
    if len(arr.shape) == 1:
        arr = arr.unsqueeze(0)
    return arr.tolist()

def dummy_embed(_):
    return [0.0] * 768

# ───── Point ID Helper ─────
def make_point_id(path, chunk_start):
    h = hashlib.sha256((path + chunk_start).encode()).hexdigest()
    return int(h, 16) % (10 ** 12)

# ───── Repo Extraction ─────
def extract_repo_from_path(json_file: Path):
    parts = json_file.parts
    try:
        output_idx = parts.index("output")
        repo = parts[output_idx + 1]
        return repo
    except Exception:
        return json_file.parent.name

# ───── Main Indexing ─────
def main():
    if not QDRANT_API_KEY:
        raise RuntimeError("QDRANT__SERVICE__API_KEY is not set in the environment or .env.qdrant!")
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)

    if client.collection_exists(COLLECTION):
        print(f"Collection '{COLLECTION}' already exists. Deleting...")
        client.delete_collection(COLLECTION)
    print(f"Creating collection '{COLLECTION}'...")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print(f"Collection '{COLLECTION}' created.")

    all_json_files = [p for p in DATA_DIR.rglob("*") if p.suffix in INCLUDE_SUFFIXES and p.is_file()]
    print(f"Found {len(all_json_files)} JSON files to process.")

    log_excluded = []
    log_included = []
    total_records = 0
    file_counter = 0
    for json_file in tqdm(all_json_files, desc="Counting records", unit="file"):
        file_counter += 1
        if not should_include(json_file):
            log_excluded.append((str(json_file), "filter"))
            continue
        kind = tag_kind(json_file)
        if kind not in {"source", "test"}:
            log_excluded.append((str(json_file), f"kind={kind}"))
            continue
        log_included.append((str(json_file), kind))
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            logging.warning(f"Failed to load {json_file}: {e}")
            continue
        entries = data if isinstance(data, list) else [data]
        for feat in entries:
            text = feat.get("source", "")
            # Always use sliding_windows_tokenizer to get windows of <=512 tokens
            token_windows = list(sliding_windows_tokenizer(text))
            total_records += max(1, len(token_windows))
        if file_counter % 1000 == 0:
            print(f"Counted {file_counter}/{len(all_json_files)} files...")

    batch_token_windows = []
    batch_payloads = []
    batch_point_ids = []
    batch = []
    records_processed = 0
    point_id_seen = set()
    skipped_files = []

    file_counter = 0
    for json_file in tqdm(all_json_files, desc="Processing JSON files"):
        if not should_include(json_file):
            continue
        kind = tag_kind(json_file)
        if kind not in {"source", "test"}:
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            logging.warning(f"Failed to load {json_file}: {e}")
            skipped_files.append(str(json_file))
            continue
        repo = extract_repo_from_path(json_file)
        entries = data if isinstance(data, list) else [data]
        for feat in entries:
            text = feat.get("source", "")
            token_windows = list(sliding_windows_tokenizer(text))
            for token_window in token_windows or [None]:
                if token_window is not None:
                    if token_window.shape[0] > 512:
                        warning_msg = f"Skipping chunk in {json_file} (tokens: {token_window.shape[0]}) > 512 tokens."
                        print(warning_msg)
                        logging.warning(warning_msg)
                        continue
                    chunk_start = tok.decode(token_window[:32], skip_special_tokens=True)
                else:
                    token_window = torch.tensor([], dtype=torch.long)
                    chunk_start = ""
                payload = {
                    "repo": repo,
                    "path": feat.get("filepath", ""),
                    "lang": feat.get("lang", ""),
                    **{k: feat[k] for k in ("group", "notes") if k in feat},
                    "chunk_start": chunk_start,
                    "kind": kind
                }
                point_id = make_point_id(payload["path"], payload["chunk_start"])
                if point_id in point_id_seen:
                    continue  # avoid accidental dups
                point_id_seen.add(point_id)
                batch_token_windows.append(token_window)
                batch_payloads.append(payload)
                batch_point_ids.append(point_id)
                if len(batch_token_windows) >= BATCH_SIZE:
                    try:
                        vectors = embed_code_batch(batch_token_windows)
                    except Exception as e:
                        logging.error(f"Embedding batch failed: {e}")
                        vectors = [dummy_embed("") for _ in batch_token_windows]
                    batch = [PointStruct(id=pid, vector=vec, payload=pld) for pid, vec, pld in zip(batch_point_ids, vectors, batch_payloads)]
                    records_processed += len(batch)
                    percent = 100.0 * records_processed / max(1, total_records)
                    batch_num = records_processed // BATCH_SIZE
                    total_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE
                    print(f"Upserting batch {batch_num}/{total_batches}: {records_processed}/{total_records} ({percent:.2f}%) complete")
                    logging.info(f"Upserting batch {batch_num}/{total_batches}: {records_processed}/{total_records} ({percent:.2f}%) complete")
                    try:
                        client.upsert(collection_name=COLLECTION, points=batch)
                    except Exception as e:
                        logging.error(f"Batch upsert failed: {e}")
                    batch_token_windows = []
                    batch_payloads = []
                    batch_point_ids = []
        if not token_windows:
            payload = {
                "repo": repo,
                "path": feat.get("filepath", ""),
                "lang": feat.get("lang", ""),
                **{k: feat[k] for k in ("group", "notes") if k in feat},
                "chunk_start": "",
                "kind": kind
            }
            point_id = make_point_id(payload["path"], payload["chunk_start"])
            if point_id not in point_id_seen:
                vector = dummy_embed("")
                batch.append(PointStruct(id=point_id, vector=vector, payload=payload))
                point_id_seen.add(point_id)
                records_processed += 1
                if len(batch) >= BATCH_SIZE:
                    percent = 100.0 * records_processed / max(1, total_records)
                    batch_num = records_processed // BATCH_SIZE
                    total_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE
                    print(f"Upserting batch {batch_num}/{total_batches}: {records_processed}/{total_records} ({percent:.2f}%) complete")
                    logging.info(f"Upserting batch {batch_num}/{total_batches}: {records_processed}/{total_records} ({percent:.2f}%) complete")
                    try:
                        client.upsert(collection_name=COLLECTION, points=batch)
                    except Exception as e:
                        logging.error(f"Batch upsert failed: {e}")
                    batch = []

    # Final batch for token windows
    if batch_token_windows:
        try:
            vectors = embed_code_batch(batch_token_windows)
        except Exception as e:
            logging.error(f"Embedding final batch failed: {e}")
            vectors = [dummy_embed("") for _ in batch_token_windows]
        batch = [PointStruct(id=pid, vector=vec, payload=pld) for pid, vec, pld in zip(batch_point_ids, vectors, batch_payloads)]
        records_processed += len(batch)
        percent = 100.0 * records_processed / max(1, total_records)
        batch_num = (records_processed + BATCH_SIZE - 1) // BATCH_SIZE
        total_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Upserting final batch {batch_num}/{total_batches}: {records_processed}/{total_records} ({percent:.2f}%) complete")
        logging.info(f"Upserting final batch {batch_num}/{total_batches}: {records_processed}/{total_records} ({percent:.2f}%) complete")
        try:
            client.upsert(collection_name=COLLECTION, points=batch)
        except Exception as e:
            logging.error(f"Final batch upsert failed: {e}")

    if not log_included:
        print("No files were included for processing. Check your filters and input data.")
        logging.warning("No files were included for processing. Check your filters and input data.")

    print(f"Included files: {len(log_included)}")
    print(f"Excluded files: {len(log_excluded)}")
    print(f"Indexed {records_processed} records into Qdrant collection '{COLLECTION}'.")
    if skipped_files:
        print(f"Skipped {len(skipped_files)} files due to errors (see qdrant_loader.log for details).")
    print("Done.")

if __name__ == "__main__":
    main()