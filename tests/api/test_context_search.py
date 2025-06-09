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
    # Insert known test data
    test_docs = [
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/HomeController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/SupportUserAccountController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/BaseController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/ActivityLogController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/AppSettingsController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/RecipientController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/ScanCodeManagementController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/AuthenticationController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/RootController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/RemoteFacilityController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        }
    ]
    col.insert_many(test_docs)
    yield
    col.delete_many({})

def test_context_search_exact_response(setup_test_features, monkeypatch):
    # Patch FeatureQuery to use test collection
    from src.api.storage import feature_query
    orig_init = feature_query.FeatureQuery.__init__
    def test_init(self, test_mode=False):
        orig_init(self, test_mode=True)
    monkeypatch.setattr(feature_query.FeatureQuery, "__init__", test_init)

    response = client.post(
        "/v1/context/search?query=controller&k=10&repo=phg-server"
    )
    assert response.status_code == 200
    data = response.json()
    expected = [
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/HomeController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/SupportUserAccountController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/BaseController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/ActivityLogController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/AppSettingsController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/RecipientController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/ScanCodeManagementController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/AuthenticationController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/RootController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        },
        {
            "repo": "phg-server",
            "program": "plx",
            "group": "Controller",
            "value": "/Users/806630/Documents/dev/plx/phg-server/src/Pharmogistics.Api/Controllers/RemoteFacilityController.cs",
            "snippet": None,
            "lang": None,
            "score": 1.5384615384615383
        }
    ]
    # Compare only the first 10 results for exact match, ignoring order
    actual_set = {tuple(sorted(item.items())) for item in data[:10]}
    expected_set = {tuple(sorted(item.items())) for item in expected}
    assert actual_set == expected_set
    # Do NOT compare lists for order, only compare sets for content
    # (Removed any list-based assertion)
    # If you want to debug, print the difference:
    if actual_set != expected_set:
        print("Missing in actual:", expected_set - actual_set)
        print("Extra in actual:", actual_set - expected_set)
