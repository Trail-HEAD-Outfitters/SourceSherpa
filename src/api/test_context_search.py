import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_context_search():
    # This test assumes Mongo is running and extract_load_summaries.py has been executed
    response = client.post(
        "/v1/context/search?query=controller&equired&k=10&repo=phg-server"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Optionally, check for expected fields in the first result
    if data:
        for field in ["repo", "program", "group", "value", "score"]:
            assert field in data[0]
    # Optionally, check that all results are for the correct repo
    for hit in data:
        assert hit["repo"] == "phg-server"

def test_context_search_exact_response():
    response = client.post(
        "/v1/context/search?query=controller&equired&k=10&repo=phg-server"
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
    # If you want to debug, print the difference:
    if actual_set != expected_set:
        print("Missing in actual:", expected_set - actual_set)
        print("Extra in actual:", actual_set - expected_set)
    # Do NOT compare lists for order, only compare sets for content
