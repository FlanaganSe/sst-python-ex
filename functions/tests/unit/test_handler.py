"""Unit tests for the simplified handler."""

import json

from src.functions.handler import (
    get_route_info,
    handle_echo,
    handle_health,
    handle_root,
    handle_time,
    make_response,
    parse_request,
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_parse_request_with_json(self):
        """Test parsing valid JSON request body."""
        event = {"body": json.dumps({"key": "value"})}
        result = parse_request(event)
        assert result == {"key": "value"}

    def test_parse_request_with_invalid_json(self):
        """Test parsing invalid JSON falls back to string."""
        event = {"body": "not json"}
        result = parse_request(event)
        assert result == {"message": "not json"}

    def test_parse_request_empty_body(self):
        """Test parsing empty body."""
        event = {}
        result = parse_request(event)
        assert result == {}

    def test_get_route_info(self):
        """Test extracting route information."""
        event = {"requestContext": {"http": {"method": "POST"}}, "rawPath": "/test"}
        method, path = get_route_info(event)
        assert method == "POST"
        assert path == "/test"

    def test_make_response_success(self):
        """Test creating successful response."""
        response = make_response(200, {"test": "data"})

        assert response["statusCode"] == 200
        assert "Access-Control-Allow-Origin" in response["headers"]

        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["data"] == {"test": "data"}

    def test_make_response_error(self):
        """Test creating error response."""
        response = make_response(400, error="Bad request")

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"] == "Bad request"


class TestRouteHandlers:
    """Test individual route handlers."""

    def test_handle_root(self):
        """Test root endpoint handler."""
        response = handle_root()

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "SST Python API" in body["data"]["message"]

    def test_handle_health(self, mock_lambda_context):
        """Test health endpoint handler."""
        response = handle_health(mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["data"]["status"] == "healthy"
        assert body["data"]["function"] == "test-function"

    def test_handle_echo(self):
        """Test echo endpoint handler."""
        test_data = {"message": "test", "metadata": {"key": "value"}}
        response = handle_echo(test_data)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["data"]["echo"] == test_data

    def test_handle_time(self):
        """Test time endpoint handler."""
        response = handle_time()

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "current_time" in body["data"]
        assert "epoch" in body["data"]
        assert body["data"]["timezone"] == "UTC"
