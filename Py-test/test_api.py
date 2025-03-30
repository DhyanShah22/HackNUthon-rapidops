import pytest
import requests
import json
import os
import datetime

LOG_FILE = "log.txt"

def log_test_case(test_case, result, error=""):
    """Logs test case execution details."""
    with open(LOG_FILE, "a") as log:
        log.write(f"Timestamp: {datetime.datetime.now()}\n")
        log.write(f"Test Case: {json.dumps(test_case, indent=4)}\n")
        log.write(f"Result: {'✅ Passed' if result else '❌ Failed'}\n")
        if error:
            log.write(f"Error: {error}\n")
        log.write("="*50 + "\n")

# Example test execution
test_case = {
    "api_endpoint": "/api/user/login",
    "method": "POST",
    "payload": {"email": "test@example.com", "password": "SecurePass123"},
    "expected_status": 200
}

try:
    # Simulate test execution
    response_status = 200  # Replace with actual API call result
    log_test_case(test_case, response_status == test_case["expected_status"])
except Exception as e:
    log_test_case(test_case, False, str(e))

try:
    # Simulate test execution
    response_status = 200  # Replace with actual API call result
    log_test_case(test_case, response_status == test_case["expected_status"])
except Exception as e:
    log_test_case(test_case, False, str(e))


# Load test cases from JSON file
with open("GenerateTestCase/data/test_cases.json", "r") as file:
    test_cases = json.load(file)

BASE_URL = "https://hack-n-uthon-6-0.vercel.app/"  # Update this if the API runs on a different port

FAILED_TESTS_FILE = "test_reports/failed_test_cases.json"

# Ensure the reports directory exists
os.makedirs("test_reports", exist_ok=True)

failed_tests = []  # Store failed test cases

@pytest.mark.parametrize("test_case", test_cases)
def test_api(test_case):
    """Dynamically test API endpoints from test_cases.json."""
    url = BASE_URL + test_case["api_endpoint"]
    method = test_case["method"]
    payload = test_case.get("payload", {})
    expected_status = test_case["expected_status"]
    expected_keys = test_case.get("expected_response_keys", [])

    try:
        response = requests.request(method, url, json=payload)

        # Log the response for debugging
        print(f"\nRequest: {method} {url}")
        print(f"Payload: {payload}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Assertions
        if response.status_code != expected_status:
            failed_tests.append(
                {
                    "api_endpoint": test_case["api_endpoint"],
                    "method": method,
                    "payload": payload,
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "error": f"Expected {expected_status}, got {response.status_code}",
                }
            )
            pytest.fail(f"❌ Expected {expected_status}, but got {response.status_code}")

        if expected_keys:
            response_json = response.json()
            missing_keys = [key for key in expected_keys if key not in response_json]
            if missing_keys:
                failed_tests.append(
                    {
                        "api_endpoint": test_case["api_endpoint"],
                        "method": method,
                        "expected_keys": expected_keys,
                        "missing_keys": missing_keys,
                        "error": f"Missing keys in response: {missing_keys}",
                    }
                )
                pytest.fail(f"❌ Missing keys in response: {missing_keys}")

    except requests.exceptions.RequestException as e:
        failed_tests.append(
            {
                "api_endpoint": test_case["api_endpoint"],
                "method": method,
                "error": str(e),
            }
        )
        pytest.fail(f"❌ API Request failed: {e}")

    except json.JSONDecodeError:
        failed_tests.append(
            {
                "api_endpoint": test_case["api_endpoint"],
                "method": method,
                "error": "Response is not valid JSON",
            }
        )
        pytest.fail("❌ Response is not valid JSON")

    except Exception as e:
        failed_tests.append(
            {
                "api_endpoint": test_case["api_endpoint"],
                "method": method,
                "error": str(e),
            }
        )
        pytest.fail(f"❌ Unexpected error: {e}")

# Save failed test cases to a file after all tests are run
@pytest.fixture(scope="session", autouse=True)
def save_failed_tests(request):
    def write_failed_tests():
        if failed_tests:
            with open(FAILED_TESTS_FILE, "w") as file:
                json.dump(failed_tests, file, indent=4)

    request.addfinalizer(write_failed_tests)