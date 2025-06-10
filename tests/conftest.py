# tests/conftest.py
import os
import sys
from pathlib import Path
import tempfile
import shutil
import pytest
from fastapi.testclient import TestClient

# ------------------------------------------------------------------
# 1. Ensure repo root is on PYTHONPATH (your original code)
# ------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]   # project root
sys.path.append(str(ROOT_DIR))

# ------------------------------------------------------------------
# 2. Shared pytest fixtures
# ------------------------------------------------------------------
@pytest.fixture(scope="session")
def sample_dir() -> Path:
    """
    Directory that holds tiny source files used by extractor unit-tests.
    E.g. tests/data/sample.cs, sample.tsx, etc.
    """
    return ROOT_DIR / "tests" / "data"

@pytest.fixture(scope="function")
def temp_out_dir():
    """
    Disposable directory for batch extractor output; auto-destroy.
    """
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    FastAPI test client – avoids launching Uvicorn.
    Monkey-patch FeatureQuery / CodeQuery in individual tests
    so Mongo/Qdrant aren’t required on CI runs.
    """
    from src.api.app import app   # adjust module path if needed
    return TestClient(app)