"""Main Lambda handler for the API function.

This module serves as the entry point for the Lambda function and dispatches
requests to appropriate handlers based on HTTP method and path.
"""

import traceback
from typing import Any

from .responses import error_response
from .router import dispatch_request
from .utils import extract_request_info, log_event


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Main Lambda handler that routes requests to appropriate handlers.

    This function is called by AWS Lambda when the function is invoked.
    It extracts the HTTP method and path from the event and dispatches
    the request to the appropriate handler.

    Args:
        event: AWS Lambda event containing request information
        context: AWS Lambda context object

    Returns:
        HTTP response dictionary with statusCode, headers, and body
    """
    try:
        # Log the incoming event (with sensitive data masked)
        log_event(event)

        # Extract request information
        request_info = extract_request_info(event)
        method = request_info["method"]
        path = request_info["path"]

        # Dispatch to appropriate handler
        return dispatch_request(method, path, event, context)

    except Exception as e:
        # Log the full traceback for debugging
        print(f"Unhandled error in Lambda handler: {traceback.format_exc()}")

        # Return a generic error response
        return error_response(500, f"Internal server error: {e!s}")
