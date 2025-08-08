"""Utility functions for Lambda handlers."""

import base64
import json
from typing import Any


def parse_body(event: dict[str, Any]) -> Any:
    """Parse request body, handling base64 encoding if necessary."""
    body = event.get("body")
    if not body:
        return None

    is_base64 = event.get("isBase64Encoded", False)
    if is_base64:
        body = base64.b64decode(body).decode("utf-8")

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def extract_request_info(event: dict[str, Any]) -> dict[str, str]:
    """Extract HTTP method and path from Lambda event."""
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")

    return {
        "method": method,
        "path": path,
    }


def get_context_info(context: Any) -> dict[str, Any]:
    """Safely extract information from Lambda context."""
    if not context:
        return {"context_info": "not_available"}

    try:
        return {
            "remaining_time_ms": context.get_remaining_time_in_millis(),
            "memory_limit_mb": context.memory_limit_in_mb,
            "function_name": context.function_name,
            "function_version": context.function_version,
            "request_id": context.aws_request_id,
        }
    except AttributeError as e:
        print(f"Context attributes not available: {e}")
        return {"context_info": "limited"}


def log_event(event: dict[str, Any]) -> None:
    """Log incoming Lambda event (with sensitive data removed)."""
    # Create a copy for logging without sensitive headers
    safe_event = event.copy()

    # Remove or mask sensitive headers if present
    if "headers" in safe_event and isinstance(safe_event["headers"], dict):
        headers = safe_event["headers"].copy()
        for sensitive_header in ["authorization", "x-api-key", "cookie"]:
            if sensitive_header in headers:
                headers[sensitive_header] = "[MASKED]"
        safe_event["headers"] = headers

    print(f"Received event: {json.dumps(safe_event)}")
