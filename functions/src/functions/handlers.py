"""Route handlers for the API Lambda function."""

import os
from datetime import datetime
from typing import Any

import httpx
from strands import Agent
from strands.models import BedrockModel

from .responses import error_response, success_response
from .utils import get_context_info, parse_body


def handle_root(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET / - Root endpoint."""
    request_info = {
        "method": event.get("requestContext", {}).get("http", {}).get("method", "GET"),
        "path": event.get("rawPath", "/"),
    }

    return success_response(
        {
            "message": "Hello from Python Lambda!",
            "stage": event.get("stageVariables", {}).get("stage", "unknown"),
            "path": request_info["path"],
            "method": request_info["method"],
            "version": "1.0.0",
        }
    )


def handle_health(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /health - Health check endpoint."""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Add Lambda context information
    context_info = get_context_info(context)
    health_data.update(context_info)

    return success_response(health_data)


def handle_echo(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle POST /echo - Echo back the request body."""
    body = parse_body(event)

    return success_response(
        {
            "echo": body,
            "headers": event.get("headers", {}),
            "method": event.get("requestContext", {}).get("http", {}).get("method"),
            "contentType": event.get("headers", {}).get("content-type", "unknown"),
        }
    )


def handle_test_params(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /test-params - Test query and path parameters."""
    return success_response(
        {
            "queryParams": event.get("queryStringParameters") or {},
            "pathParams": event.get("pathParameters") or {},
            "multiValueQueryParams": event.get("multiValueQueryStringParameters") or {},
        }
    )


def handle_time(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /time - Current time endpoint."""
    return success_response(
        {
            "current_time": datetime.utcnow().isoformat(),
            "timezone": "UTC",
            "epoch": int(datetime.utcnow().timestamp()),
            "function_name": getattr(context, "function_name", None) if context else None,
        }
    )


def handle_error(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /error - Intentional error for testing."""
    raise Exception("Intentional test error for debugging purposes")


def handle_options(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle OPTIONS requests for CORS preflight."""
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token",
            "Access-Control-Max-Age": "86400",
        },
        "body": "",
    }


def handle_fetch_example(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /fetch - Example of using httpx to make HTTP requests."""
    try:
        # Example: Fetch data from a public API
        url = "https://httpbin.org/json"

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()

            api_data = response.json()

        return success_response(
            {
                "message": "Successfully fetched data using httpx",
                "external_api_data": api_data,
                "httpx_version": httpx.__version__,
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
            }
        )

    except httpx.RequestError as e:
        return error_response(503, f"Network error: {e}")
    except httpx.HTTPStatusError as e:
        return error_response(502, f"HTTP error: {e.response.status_code}")
    except Exception as e:
        return error_response(500, f"Unexpected error: {e}")


def handle_strands_query(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle POST /strands - Use Strands AI to query AWS Nova Lite model."""
    try:
        # Parse the request body to get the user query
        body = parse_body(event)

        if not body or "query" not in body:
            return error_response(400, "Missing 'query' field in request body")

        user_query = body["query"]

        if not user_query or not isinstance(user_query, str):
            return error_response(400, "Query must be a non-empty string")

        bedrock_model = BedrockModel(
            model_id="amazon.nova-lite-v1:0",  # or "amazon.nova-pro-v1:0"
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            # optional knobs:
            # temperature=0.2, top_p=0.9, streaming=True
        )
        agent = Agent(model=bedrock_model)

        # Make the request to the model
        response = agent(user_query)

        return success_response(
            {
                "query": user_query,
                "response": response,
                "model": "aws-nova-lite",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        # Log the full error for debugging
        error_msg = f"Strands AI error: {e!s}"
        return error_response(500, error_msg)
