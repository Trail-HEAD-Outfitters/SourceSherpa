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
from typing import List, Dict, Any
import os
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config.settings import settings

class FeatureLoader:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_database]
        self.collection = self.db["features"]

def load_features(input_path: Path, test_mode=False):
    collection_name = "features_test" if test_mode else "features"
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
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