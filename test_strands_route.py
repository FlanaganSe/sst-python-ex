#!/usr/bin/env python3
"""
Test script for the new Strands AI route.
This script simulates a Lambda event and tests the handle_strands_query function.
"""

import json
import sys
from pathlib import Path

from functions.handlers import handle_strands_query

# Add the functions package to the path
functions_path = Path(__file__).parent / "functions" / "src"
sys.path.insert(0, str(functions_path))


def test_strands_query():
    """Test the Strands AI query handler."""

    # Create a mock Lambda event
    mock_event = {
        "requestContext": {"http": {"method": "POST"}},
        "body": json.dumps({"query": "What is the capital of France? Please provide a brief answer."}),
        "headers": {"content-type": "application/json"},
    }

    # Mock Lambda context (can be None for testing)
    mock_context = None

    print("Testing Strands AI route...")
    print(f"Query: {json.loads(mock_event['body'])['query']}")
    print("-" * 50)

    try:
        # Call the handler
        response = handle_strands_query(mock_event, mock_context)

        print("Response received:")
        print(f"Status Code: {response.get('statusCode')}")

        if response.get("body"):
            body = json.loads(response["body"])
            print(f"Success: {body.get('success', False)}")

            if body.get("success"):
                print(f"AI Response: {body.get('data', {}).get('response')}")
                print(f"Model: {body.get('data', {}).get('model')}")
            else:
                print(f"Error: {body.get('error')}")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_strands_query()
