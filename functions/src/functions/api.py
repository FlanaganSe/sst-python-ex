import json
from typing import Any, Dict

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simple Lambda handler for testing deployment."""
    
    # Log the incoming event for debugging
    print(f"Received event: {json.dumps(event)}")
    
    # Simple response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "message": "Hello from Python Lambda!",
            "stage": event.get("stageVariables", {}).get("stage", "unknown"),
            "path": event.get("rawPath", "/"),
        }),
    }