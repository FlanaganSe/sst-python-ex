# SST Python AI API — Agent Guide

Concise guide for AI agents working in this repo. Keep edits minimal, follow existing patterns, and ensure tests pass.

## Essentials

- Entry point: `functions/src/functions/handler.py:handler`
- Infra: `sst.config.ts` (Function URL, CORS, env, perms)
- Tests: `functions/tests/{unit,integration}`

## Stack

- Python 3.12 (ARM64) Lambda
- Strands `Agent` + `BedrockModel` (Nova Lite)
- httpx, pydantic v2, AWS Lambda Powertools
- Tooling: UV, Ruff, mypy, pytest

## Routes

```
(GET, "/")        → handle_root()
(GET, "/health")   → handle_health(context)
(POST, "/echo")    → handle_echo(parse_request(event))
(GET, "/time")     → handle_time()
(GET, "/fetch")    → handle_fetch()
(POST, "/strands") → handle_ai_query(parse_request(event))
(GET, "/error")    → handle_error()
(OPTIONS, "*")      → handle_options()
```

## Response Contract

- Envelope: `{ success: bool, timestamp: str, data?: {}, error?: str }`
- Use `make_response(status, data?, error?)` for CORS + JSON

## Configuration (config.py)

- `STAGE` default `dev`; `AWS_REGION` default `us-east-1`
- `AWS_LAMBDA_FUNCTION_NAME` set by Lambda
- `BEDROCK_MODEL_ID` default `amazon.nova-lite-v1:0`
- `AI_TIMEOUT` default `30`; `REQUEST_TIMEOUT` is `10` seconds in code

## Bedrock Permissions

- Granted in `sst.config.ts`:
  `bedrock:Converse`, `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`
- Change model via `BEDROCK_MODEL_ID` or in code

## Commands

- Setup: `pnpm setup`
- Dev: `pnpm dev`
- Deploy/Remove: `pnpm aws:deploy` / `pnpm aws:remove`
- Tests: `pnpm test`, `pnpm test:all`, `pnpm test:cov`
- Quality: `pnpm quality` (lint + typecheck + unit tests)

## Testing

- Unit: test pure handlers/utilities
- Integration: call `handler(event, context)` end-to-end
- Mocks:
  - External HTTP: `@patch("src.functions.handler.httpx.Client")`
  - AI calls: `@patch("src.functions.handler.Agent")`
- Fixtures: `functions/tests/conftest.py` (events, `mock_lambda_context`)

## Modifying Endpoints

- Add function in `handler.py` and register in `ROUTES`
- For POST, parse with `parse_request(event)`
- Always return `make_response(...)`
- Add/adjust tests under `functions/tests`

## Dependencies

- Python: edit `functions/pyproject.toml` → `uv sync`
- Node (infra): edit `package.json` / `sst.config.ts`

## AI Call Shape

- Request: `{ "query": str, "metadata"?: {} }`
- Handler: `Agent(BedrockModel(...))(query)`
- Errors: validation → 400; AI/service → 502; unhandled → 500

## Gotchas

- Bedrock Nova access must be enabled in the target AWS account/region
- Ensure `uv sync` after changing Python deps
- Responses must be JSON-serializable; use `model_dump_json()` via `APIResponse`
- Keep `OPTIONS *` route for CORS preflight
