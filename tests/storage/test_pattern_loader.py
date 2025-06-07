import subprocess
from pymongo import MongoClient

MONGO_URI = "mongodb://root:password@localhost:27017/"
DB_NAME = "code_routing"
COLLECTION = "patterns_test"

def clear_patterns():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    db[COLLECTION].delete_many({})

def test_pattern_loader_script():
    clear_patterns()
    result = subprocess.run(
        ["python", "src/storage/pattern_loader.py", "--test"],
        capture_output=True,
        text=True,
    )
    print("\nPattern Loader STDOUT:", result.stdout)
    print("\nPattern Loader STDERR:", result.stderr)
    assert result.returncode == 0, "Pattern loader exited with error!"
    assert ("Inserted" in result.stdout or "already populated" in result.stdout), "Pattern loader did not report success!"
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    assert db[COLLECTION].count_documents({}) > 0, "No documents found in patterns_test after loader ran!"
    clear_patterns()