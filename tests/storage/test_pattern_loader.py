import subprocess
from pymongo import MongoClient
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.config.settings import settings

COLLECTION = "patterns_test"

def clear_patterns():
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    db[COLLECTION].delete_many({})

def test_pattern_loader_script():
    clear_patterns()
    result = subprocess.run(
        ["python", str(project_root / "src/storage/pattern_loader.py"), "--test"],
        capture_output=True,
        text=True,
    )
    print("\nPattern Loader STDOUT:", result.stdout)
    print("\nPattern Loader STDERR:", result.stderr)
    assert result.returncode == 0, "Pattern loader exited with error!"
    assert ("Inserted" in result.stdout or "already populated" in result.stdout), "Pattern loader did not report success!"
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    assert db[COLLECTION].count_documents({}) > 0, "No documents found in patterns_test after loader ran!"
    clear_patterns()