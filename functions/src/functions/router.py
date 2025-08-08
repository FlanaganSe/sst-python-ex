"""Route configuration and dispatcher for the API Lambda function."""

from collections.abc import Callable
from typing import Any

from .handlers import (
    handle_echo,
    handle_error,
    handle_fetch_example,
    handle_health,
    handle_options,
    handle_root,
    handle_strands_query,
    handle_test_params,
    handle_time,
)
from .responses import not_found_response

# Route configuration
ROUTES: dict[tuple[str, str], Callable[[dict[str, Any], Any], dict[str, Any]]] = {
    ("GET", "/"): handle_root,
    ("GET", "/health"): handle_health,
    ("POST", "/echo"): handle_echo,
    ("GET", "/test-params"): handle_test_params,
    ("GET", "/time"): handle_time,
    ("GET", "/error"): handle_error,
    ("GET", "/fetch"): handle_fetch_example,  # New httpx example endpoint
    ("POST", "/strands"): handle_strands_query,  # New Strands AI endpoint
    ("OPTIONS", "*"): handle_options,  # Handle all OPTIONS requests
}


def dispatch_request(method: str, path: str, event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Dispatch request to appropriate handler based on method and path."""

    # Handle OPTIONS requests for any path
    if method == "OPTIONS":
        return handle_options(event, context)

    # Look for exact route match
    route_key = (method, path)
    if route_key in ROUTES:
        handler = ROUTES[route_key]
        return handler(event, context)

    # No route found
    return not_found_response(path, method)
