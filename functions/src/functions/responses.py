"""Response utilities for Lambda functions."""

import json
from typing import Any


def success_response(data: Any) -> dict[str, Any]:
    """Create a successful HTTP response."""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": json.dumps(data, default=str),
    }


def error_response(status_code: int, message: str) -> dict[str, Any]:
    """Create an error HTTP response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": json.dumps({"error": message, "statusCode": status_code}),
    }


def not_found_response(path: str, method: str) -> dict[str, Any]:
    """Create a 404 not found response."""
    return error_response(404, f"Route not found: {method} {path}")
