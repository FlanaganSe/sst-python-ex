import json
import traceback
from typing import Any


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler with multiple test endpoints for API testing."""

    # Log the incoming event
    print(f"Received event: {json.dumps(event)}")

    # Extract HTTP method and path
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")

    # Route handling
    try:
        # GET /
        if method == "GET" and path == "/":
            return success_response(
                {
                    "message": "Hello from Python Lambda!",
                    "stage": event.get("stageVariables", {}).get("stage", "unknown"),
                    "path": path,
                    "method": method,
                }
            )

        # GET /health
        elif method == "GET" and path == "/health":
            # Safely access context attributes
            health_data = {
                "status": "healthy",
            }

            # Add context info if available
            if context:
                try:
                    health_data.update(
                        {
                            "remaining_time_ms": context.get_remaining_time_in_millis(),
                            "memory_limit_mb": context.memory_limit_in_mb,
                            "function_name": context.function_name,
                            "function_version": context.function_version,
                            "request_id": context.aws_request_id,
                        }
                    )
                except AttributeError as e:
                    # If context doesn't have expected attributes, just log it
                    print(f"Context attributes not available: {e}")
                    health_data["context_info"] = "limited"

            return success_response(health_data)

        # POST /echo
        elif method == "POST" and path == "/echo":
            body = parse_body(event)
            return success_response(
                {
                    "echo": body,
                    "headers": event.get("headers", {}),
                }
            )

        # GET /test-params
        elif method == "GET" and path == "/test-params":
            params = event.get("queryStringParameters", {})
            return success_response(
                {
                    "queryParams": params,
                    "pathParams": event.get("pathParameters", {}),
                }
            )

        # GET /time (adding this useful endpoint)
        elif method == "GET" and path == "/time":
            from datetime import datetime

            return success_response(
                {
                    "current_time": datetime.utcnow().isoformat(),
                    "timezone": "UTC",
                    "function_name": getattr(context, "function_name", None) if context else None,
                }
            )

        # GET /error (intentional error for testing)
        elif method == "GET" and path == "/error":
            raise Exception("Intentional test error")

        # 404 for unknown routes
        else:
            return error_response(404, f"Route not found: {method} {path}")

    except Exception as e:
        print(f"Error handling request: {traceback.format_exc()}")
        return error_response(500, str(e))


def parse_body(event: dict[str, Any]) -> Any:
    """Parse request body, handling base64 encoding if necessary."""
    body = event.get("body")
    if not body:
        return None

    is_base64 = event.get("isBase64Encoded", False)
    if is_base64:
        import base64

        body = base64.b64decode(body).decode("utf-8")

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def success_response(data: Any) -> dict[str, Any]:
    """Create a successful response."""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data, default=str),
    }


def error_response(status_code: int, message: str) -> dict[str, Any]:
    """Create an error response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"error": message}),
    }
