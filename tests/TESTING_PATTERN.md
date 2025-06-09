# API Endpoint Test Pattern: Isolated, Deterministic, and Repeatable

## Why?

To ensure API endpoint tests are reliable and not affected by production or variable data, use a controlled test dataset and a dedicated test collection. This makes tests deterministic, repeatable, and robust.

## Pattern Steps

1. **Fixture for Test Data**
   - Use a pytest fixture to insert a known set of documents into a test collection (e.g., `features_test`) before the test runs, and remove them after.

2. **Patch Data Access Layer**
   - Patch the data access class (e.g., `FeatureQuery`) to use the test collection instead of the production one during the test.

3. **Run the Test**
   - Call the API endpoint using FastAPI's `TestClient`.
   - Assert the response matches the expected data (ignoring order if needed).

4. **Cleanup**
   - The fixture automatically cleans up the test data after the test.

## Example

```python
import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from src.api.app import app
from src.config.settings import settings

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_test_features():
    client_mongo = MongoClient(settings.mongodb_uri)
    db = client_mongo[settings.mongodb_database]
    col = db["features_test"]
    col.delete_many({})
    test_docs = [
        {"repo": "phg-server", "program": "plx", "group": "Controller", "value": "...", "snippet": None, "lang": None, "score": 1.0},
        # ... more test docs ...
    ]
    col.insert_many(test_docs)
    yield
    col.delete_many({})

def test_context_search_exact_response(setup_test_features, monkeypatch):
    from src.api.storage import feature_query
    orig_init = feature_query.FeatureQuery.__init__
    def test_init(self, test_mode=False):
        orig_init(self, test_mode=True)
    monkeypatch.setattr(feature_query.FeatureQuery, "__init__", test_init)

    response = client.post("/v1/context/search?query=controller&k=10&repo=phg-server")
    assert response.status_code == 200
    data = response.json()
    # ...assertions on data...
```

## Benefits
- **Isolation:** No dependency on production or variable data.
- **Repeatability:** Test always runs against the same dataset.
- **Cleanup:** No leftover test data.
- **Determinism:** Assertions are reliable and not flaky.

## When to Use
- For any API endpoint test that depends on database state.
- When you need to assert exact response content.

---

_See `test_context_search.py` for a real example._
