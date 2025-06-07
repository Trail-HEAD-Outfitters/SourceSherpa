import subprocess
from pymongo import MongoClient
from pathlib import Path

MONGO_URI = "mongodb://root:password@localhost:27017/"
DB_NAME = "code_routing"
COLLECTION = "features_test"

def clear_features():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    db[COLLECTION].delete_many({})

def test_feature_loader_script():
    clear_features()
    # Point to your static test data file:
    test_data_file = Path("tests/storage/test_data/test_features_and_patterns.json")
    assert test_data_file.exists(), f"Test data file {test_data_file} does not exist!"

    result = subprocess.run(
        [
            "python", "src/storage/feature_loader.py",
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

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    doc_count = db[COLLECTION].count_documents({})
    assert doc_count > 0, f"Feature loader did not insert any documents! (count={doc_count})"
    clear_features()