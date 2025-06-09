# scripts/dev_run_toc.py
from pathlib import Path
import importlib
import json
from pymongo import MongoClient
from src.config.settings import settings

# 1) run extractor ----------------------------------------------------------------
toc_mod = importlib.import_module("src.extractors.code_summary_extractor")
toc     = toc_mod.TOCExtractor(debug=True)
toc.walk()
toc.save()

out_json = toc_mod.OUT_FILE          # the Path object written by extractor
print(f"\n✅  Extractor wrote: {out_json}  ({out_json.stat().st_size/1024:.1f} KB)")

# 2) load into Mongo --------------------------------------------------------------
loader_mod = importlib.import_module("src.storage.feature_loader")
client      = MongoClient(settings.mongodb_uri)
db          = client[settings.mongodb_database]
features    = db["features"]
features.delete_many({})
print("🧹  Cleared 'features' collection.")

data = json.loads(out_json.read_text(encoding="utf-8"))
# Deduplicate features by (repo, value, hash)
unique = {}
duplicates = 0
for row in data:
    key = (row.get("repo"), row.get("value"), row.get("hash"))
    if key not in unique:
        row["source_file"] = out_json.name  # add filename like loader does
        unique[key] = row
    else:
        duplicates += 1
unique_data = list(unique.values())
print(f"🧹  Deduplicated features: {len(unique_data)} unique, {duplicates} duplicates skipped.")
features.insert_many(unique_data)
print(f"✅  Inserted {features.count_documents({})} docs into 'features'.")

# 3) quick peek -------------------------------------------------------------------
print("\n🔍  Sample doc:")
print(features.find_one({}, {"_id": 0}))