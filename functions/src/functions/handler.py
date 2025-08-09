"""Modern, concise Lambda handler for SST Python API.

A single-file approach that prioritizes simplicity, maintainability, and performance
for MVP use cases while maintaining flexibility for future expansion.
"""

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import httpx
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field, ValidationError
from strands import Agent
from strands.models import BedrockModel

from functions.config import BEDROCK_MODEL, FUNCTION_NAME, REGION, REQUEST_TIMEOUT, STAGE

# Initialize AWS services
tracer = Tracer()
logger = Logger(service="api", level="INFO")
logger.append_keys(stage=STAGE, region=REGION, function=FUNCTION_NAME)

# Type alias for route handlers
RouteHandler = Callable[[dict[str, Any], LambdaContext | None], dict[str, Any]]


# Core models for type safety
class APIRequest(BaseModel):
    """Generic API request model."""

    message: str | None = None
    query: str | None = None
    metadata: dict[str, Any] | None = None


class APIResponse(BaseModel):
    """Standard API response model."""

    success: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] | None = None
    error: str | None = None


# Constants
HTTP_SUCCESS_THRESHOLD = 400

# CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json",
}


def make_response(status: int, data: Any = None, error: str | None = None) -> dict[str, Any]:
    """Create standardized HTTP response."""
    response_data = APIResponse(success=status < HTTP_SUCCESS_THRESHOLD, data=data or {}, error=error)

    return {"statusCode": status, "headers": CORS_HEADERS, "body": response_data.model_dump_json()}


def parse_request(event: dict[str, Any]) -> dict[str, Any]:
    """Parse request body from Lambda event."""
    body = event.get("body", "{}")
    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError:
        return {"message": body}


def get_route_info(event: dict[str, Any]) -> tuple[str, str]:
    """Extract HTTP method and path from event."""
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")
    return method, path


# Route handlers
def handle_root() -> dict[str, Any]:
    """GET / - API welcome."""
    return make_response(
        200, {"message": "SST Python API", "stage": STAGE, "version": "2.0.0", "function": FUNCTION_NAME}
    )


def handle_health(context: LambdaContext | None) -> dict[str, Any]:
    """GET /health - Health check with Lambda context."""
    return make_response(
        200,
        {
            "status": "healthy",
            "function": context.function_name if context else FUNCTION_NAME,
            "memory": f"{context.memory_limit_in_mb}MB" if context else "unknown",
            "remaining_ms": context.get_remaining_time_in_millis() if context else None,
        },
    )


def handle_echo(request_data: dict[str, Any]) -> dict[str, Any]:
    """POST /echo - Echo request data."""
    return make_response(200, {"echo": request_data, "received_at": datetime.now(UTC).isoformat()})


def handle_time() -> dict[str, Any]:
    """GET /time - Current time."""
    now = datetime.now(UTC)
    return make_response(200, {"current_time": now.isoformat(), "epoch": int(now.timestamp()), "timezone": "UTC"})


def handle_fetch() -> dict[str, Any]:
    """GET /fetch - External HTTP request example."""
    start = time.time()

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get("https://httpbin.org/json")
            response.raise_for_status()
            data = response.json()

        return make_response(
            200,
            {
                "message": "External fetch successful",
                "external_data": data,
                "response_time_ms": round((time.time() - start) * 1000, 2),
                "status_code": response.status_code,
            },
        )

    except Exception as e:
        logger.exception("Fetch error", exc_info=e)
        return make_response(502, error=f"External service error: {e!s}")


def handle_ai_query(request_data: dict[str, Any]) -> dict[str, Any]:
    """POST /strands - AI query to Bedrock."""
    try:
        # Validate request
        req = APIRequest.model_validate(request_data)
        if not req.query:
            return make_response(400, error="Query is required")

        # Setup AI model
        start = time.time()
        model = BedrockModel(model_id=BEDROCK_MODEL, region_name=REGION, temperature=0.7)
        agent = Agent(model=model)

        # Make AI request
        ai_response = agent(req.query)
        response_time = round((time.time() - start) * 1000, 2)

        logger.info("AI query completed", extra={"query_length": len(req.query), "response_time_ms": response_time})

        return make_response(
            200,
            {
                "query": req.query,
                "response": str(ai_response),
                "model": BEDROCK_MODEL,
                "response_time_ms": response_time,
            },
        )

    except ValidationError as e:
        return make_response(400, error=f"Invalid request: {e}")
    except Exception as e:
        logger.exception("AI service error", exc_info=e)
        return make_response(502, error=f"AI service error: {e!s}")


class TestError(Exception):
    """Custom exception for testing purposes."""


def handle_error() -> dict[str, Any]:
    """GET /error - Test error handling."""
    logger.warning("Intentional test error")
    raise TestError("Test error for monitoring")


def handle_options() -> dict[str, Any]:
    """OPTIONS * - CORS preflight."""
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}


# Route mapping
ROUTES: dict[tuple[str, str], RouteHandler] = {
    ("GET", "/"): lambda _e, _c: handle_root(),
    ("GET", "/health"): lambda _e, c: handle_health(c),
    ("POST", "/echo"): lambda e, _c: handle_echo(parse_request(e)),
    ("GET", "/time"): lambda _e, _c: handle_time(),
    ("GET", "/fetch"): lambda _e, _c: handle_fetch(),
    ("POST", "/strands"): lambda e, _c: handle_ai_query(parse_request(e)),
    ("GET", "/error"): lambda _e, _c: handle_error(),
    ("OPTIONS", "*"): lambda _e, _c: handle_options(),
}


@tracer.capture_lambda_handler
def handler(event: dict[str, Any], context: LambdaContext | None) -> dict[str, Any]:
    """Main Lambda handler - clean, fast, and maintainable."""
    try:
        method, path = get_route_info(event)
        logger.info("Request received", extra={"method": method, "path": path})

        # Add tracing
        tracer.put_annotation("http_method", method)
        tracer.put_annotation("http_path", path)

        # Handle OPTIONS for any path
        if method == "OPTIONS":
            return handle_options()

        # Find and execute handler
        route_key = (method, path)
        if route_key in ROUTES:
            response = ROUTES[route_key](event, context)
            logger.info("Request completed", extra={"status": response["statusCode"]})
            return response

        # Route not found
        return make_response(404, error=f"Route not found: {method} {path}")

    except Exception as e:
        logger.exception("Unhandled error", exc_info=e)
        tracer.put_annotation("error_type", type(e).__name__)
        return make_response(500, error="Internal server error")
