import subprocess
from pymongo import MongoClient
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.config.settings import settings

COLLECTION = "features_test"

def clear_features():
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    db[COLLECTION].delete_many({})

def test_feature_loader_script():
    clear_features()
    test_data_file = Path(__file__).parent / "test_data/test_features_and_patterns.json"
    assert test_data_file.exists(), f"Test data file {test_data_file} does not exist!"

    result = subprocess.run(
        [
            "python", str(project_root / "src/storage/feature_loader.py"),
            "--input", str(test_data_file),
            "--test"
        ],
        capture_output=True,
        text=True,
    )
    print("\nFeature Loader STDOUT:", result.stdout)
    print("\nFeature Loader STDERR:", result.stderr)
    assert result.returncode == 0, "Feature loader exited with error!"
    assert "Inserted" in result.stdout, "Feature loader did not report success!"

    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    doc_count = db[COLLECTION].count_documents({})
    assert doc_count > 0, f"Feature loader did not insert any documents! (count={doc_count})"
    clear_features()