"""Route handlers for the API Lambda function."""

from datetime import datetime
from typing import Any

from .responses import success_response
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
