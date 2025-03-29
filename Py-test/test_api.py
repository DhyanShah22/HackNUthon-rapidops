import pytest
import requests
import json

# Load test cases from JSON file
with open("GenerateTestCase/data/test_cases.json", "r") as file:
    test_cases = json.load(file)

BASE_URL = "https://hack-n-uthon-6-0.vercel.app/"  # Update this if the API runs on a different port

@pytest.mark.parametrize("test_case", test_cases)
def test_api(test_case):
    """Dynamically test API endpoints from test_cases.json."""
    
    url = BASE_URL + test_case["api_endpoint"]
    method = test_case["method"]
    payload = test_case.get("payload", {})
    expected_status = test_case["expected_status"]
    expected_keys = test_case.get("expected_response_keys", [])

    # Make API request
    response = requests.request(method, url, json=payload)
    
    # Assertions
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    
    if expected_keys:
        response_json = response.json()
        for key in expected_keys:
            assert key in response_json, f"Key '{key}' missing in response"