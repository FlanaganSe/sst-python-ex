"""Integration tests for the simplified API Lambda function."""

import json
from unittest.mock import MagicMock, patch

import pytest
from src.functions.handler import handler


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for the complete API handler."""

    def test_root_endpoint_integration(self, sample_lambda_event, mock_lambda_context):
        """Test complete root endpoint flow."""
        response = handler(sample_lambda_event, mock_lambda_context)

        assert response["statusCode"] == 200
        assert "Content-Type" in response["headers"]
        assert "Access-Control-Allow-Origin" in response["headers"]

        body = json.loads(response["body"])
        assert body["success"] is True
        assert "SST Python API" in body["data"]["message"]

    def test_health_endpoint_integration(self, mock_lambda_context):
        """Test complete health endpoint flow."""
        event = {
            "requestContext": {"http": {"method": "GET", "path": "/health"}},
            "rawPath": "/health",
            "headers": {"user-agent": "test-client"},
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["data"]["status"] == "healthy"
        assert body["data"]["function"] == "test-function"

    def test_echo_endpoint_integration(self, mock_lambda_context):
        """Test complete echo endpoint flow."""
        event = {
            "requestContext": {"http": {"method": "POST", "path": "/echo"}},
            "rawPath": "/echo",
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"message": "integration test", "metadata": {"test": True}}),
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["data"]["echo"]["message"] == "integration test"
        assert body["data"]["echo"]["metadata"]["test"] is True

    def test_not_found_endpoint_integration(self, mock_lambda_context):
        """Test 404 handling integration."""
        event = {
            "requestContext": {"http": {"method": "GET", "path": "/nonexistent"}},
            "rawPath": "/nonexistent",
            "headers": {},
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["success"] is False
        assert "Route not found" in body["error"]

    def test_options_endpoint_integration(self, mock_lambda_context):
        """Test OPTIONS handling integration."""
        event = {
            "requestContext": {"http": {"method": "OPTIONS", "path": "/any"}},
            "rawPath": "/any",
            "headers": {},
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        assert response["body"] == ""
        assert "Access-Control-Allow-Methods" in response["headers"]

    def test_ai_query_validation_error_integration(self, mock_lambda_context):
        """Test AI query validation error handling integration."""
        event = {
            "requestContext": {"http": {"method": "POST", "path": "/strands"}},
            "rawPath": "/strands",
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"invalid_field": "value"}),
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["success"] is False
        assert "Query is required" in body["error"]

    def test_intentional_error_handling(self, mock_lambda_context):
        """Test error endpoint exception handling."""
        event = {
            "requestContext": {"http": {"method": "GET", "path": "/error"}},
            "rawPath": "/error",
            "headers": {},
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["success"] is False
        assert "Internal server error" in body["error"]

    @patch("src.functions.handler.httpx.Client")
    def test_fetch_endpoint_integration(self, mock_client, mock_lambda_context):
        """Test fetch endpoint integration."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.get.return_value = mock_response

        event = {
            "requestContext": {"http": {"method": "GET", "path": "/fetch"}},
            "rawPath": "/fetch",
            "headers": {},
        }

        response = handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "External fetch successful" in body["data"]["message"]
        assert body["data"]["external_data"]["test"] == "data"
