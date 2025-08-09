"""Pytest configuration and fixtures for the functions package."""

import json
import os
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_lambda_context():
    """Create a mock Lambda context."""
    context = MagicMock()
    context.function_name = "test-function"
    context.function_version = "$LATEST"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
    context.memory_limit_in_mb = "128"
    context.get_remaining_time_in_millis.return_value = 30000
    context.aws_request_id = "test-request-id"
    return context


@pytest.fixture
def sample_lambda_event():
    """Create a sample Lambda event for testing."""
    return {
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/",
                "sourceIp": "127.0.0.1",
            }
        },
        "rawPath": "/",
        "headers": {
            "content-type": "application/json",
            "user-agent": "test-client/1.0",
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "body": None,
        "isBase64Encoded": False,
    }


@pytest.fixture
def post_event_with_json_body(sample_lambda_event):
    """Create a POST event with JSON body."""
    event = sample_lambda_event.copy()
    event["requestContext"]["http"]["method"] = "POST"
    event["rawPath"] = "/echo"
    event["body"] = json.dumps({"message": "test message", "metadata": {"key": "value"}})
    return event


@pytest.fixture
def strands_query_event(sample_lambda_event):
    """Create a Strands AI query event."""
    event = sample_lambda_event.copy()
    event["requestContext"]["http"]["method"] = "POST"
    event["rawPath"] = "/strands"
    event["body"] = json.dumps({"query": "What is the capital of France?", "temperature": 0.7, "max_tokens": 100})
    return event


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    test_env = {
        "STAGE": "test",
        "AWS_REGION": "us-east-1",
        "AWS_LAMBDA_FUNCTION_NAME": "test-function",
    }

    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_httpx_response():
    """Mock httpx response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    mock_response.elapsed.total_seconds.return_value = 0.1
    return mock_response
