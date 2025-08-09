"""Tiny, explicit config for the Lambda function."""

import os
from typing import Literal

# Environment
STAGE: Literal["dev", "staging", "production", "test"] = os.getenv("STAGE", "dev")  # type: ignore[assignment]
REGION = os.getenv("AWS_REGION", "us-east-1")
FUNCTION_NAME = os.getenv("AWS_LAMBDA_FUNCTION_NAME", "api-function")

# AI
BEDROCK_MODEL = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "30"))

# HTTP
REQUEST_TIMEOUT = 10
