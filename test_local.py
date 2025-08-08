#!/usr/bin/env python3
"""
Local testing script for your Lambda functions.
Run this to test your handlers locally before deployment.
"""

import json
import sys
from pathlib import Path

# Add the functions source to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "functions" / "src"))

# Import your handlers
from functions.api import handler


def create_test_event(method="GET", path="/", body=None, headers=None):
    """Create a mock Lambda event for testing."""
    return {
        "requestContext": {
            "http": {
                "method": method,
                "path": path,
            }
        },
        "rawPath": path,
        "headers": headers or {},
        "body": json.dumps(body) if body else None,
    }


def create_test_context():
    """Create a mock Lambda context for testing."""

    class MockContext:
        def __init__(self):
            self.function_name = "test-function"
            self.function_version = "$LATEST"
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
            self.memory_limit_in_mb = "128"
            self.remaining_time_in_millis = lambda: 30000

    return MockContext()


def test_endpoints():
    """Test various endpoints locally."""
    context = create_test_context()

    print("🧪 Testing Lambda Functions Locally\n")

    # Test root endpoint
    print("1. Testing GET /")
    event = create_test_event("GET", "/")
    response = handler(event, context)
    print(f"   Status: {response['statusCode']}")
    print(f"   Response: {json.loads(response['body'])['message']}\n")

    # Test health endpoint
    print("2. Testing GET /health")
    event = create_test_event("GET", "/health")
    response = handler(event, context)
    print(f"   Status: {response['statusCode']}")
    body = json.loads(response["body"])
    print(f"   Status: {body['status']}")
    print(f"   Timestamp: {body['timestamp']}\n")

    # Test httpx endpoint
    print("3. Testing GET /fetch (httpx example)")
    event = create_test_event("GET", "/fetch")
    try:
        response = handler(event, context)
        print(f"   Status: {response['statusCode']}")
        body = json.loads(response["body"])
        if response["statusCode"] == 200:
            print("   ✅ httpx request successful!")
            print(f"   ✅ httpx version: {body['httpx_version']}")
            print(f"   ✅ Response time: {body['response_time_ms']:.2f}ms")
        else:
            print(f"   ❌ Error: {body}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    print("\n🎉 Local testing complete!")
    print("\nTo deploy to AWS:")
    print("   pnpm sst deploy")


if __name__ == "__main__":
    test_endpoints()
