"""
Feature Loader: Loads code features into MongoDB.

USAGE:
    python src/storage/feature_loader.py --input <path_to_features_and_patterns.json>

Expected input file format:
[
  {
    "repo": "phg-server",
    "program": "plx",
    "group": "Controller",
    "value": "src/Controllers/UserController.cs",
    "matched_pattern": "Controllers/*Controller.cs",
    "notes": "ASP.NET MVC & Web-API controllers",
    "source_file": "UserController.cs.json"
  },
  ...
]

Each item is a code feature (usually from features_and_patterns.json).
"""

import json
from pathlib import Path
import argparse
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb://root:password@localhost:27017/"
DB_NAME = "code_routing"
client = MongoClient(MONGO_URI)
db = client["code_routing"]
features_col = db["features"]

def load_features(input_path: Path, test_mode=False):
    collection_name = "features_test" if test_mode else "features"
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    features_col = db[collection_name]

    features_col.delete_many({})
    print(f"🧹 Cleared all existing features in collection '{collection_name}'.")

    if input_path.exists():
        with open(input_path, "r", encoding="utf-8") as f:
            feature_data = json.load(f)
            for item in feature_data:
                item["source_file"] = input_path.name
            features_col.insert_many(feature_data)
            print(f"✅ Inserted {len(feature_data)} features from {input_path} into collection '{collection_name}'.")
    else:
        print(f"❌ Could not find {input_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load code features into MongoDB.")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to features JSON file")
    parser.add_argument("--test", action="store_true", help="Use the _test collection")
    args = parser.parse_args()
    load_features(Path(args.input), test_mode=args.test)