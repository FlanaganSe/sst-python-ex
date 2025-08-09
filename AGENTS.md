# SST Python AI API — Agent Guide

Pragmatic notes for coding agents working in this repo. Keep it simple, precise, and stage-safe.

## Context

- Purpose: MVP/hackathon API to exercise Strands Agents on AWS Bedrock (Nova) via a single Python Lambda.
- Entry point: `functions/src/functions/handler.py:handler` (all routes in one file).
- Infra: `sst.config.ts` provisions one `sst.aws.Function` with a public URL and Bedrock permissions.

## Stack

- Runtime: Python 3.12 (ARM64) on Lambda
- AI: `strands` Agent + `BedrockModel` (Nova Lite default)
- HTTP: `httpx`
- Types/validation: `pydantic` v2
- Observability: AWS Lambda Powertools (logger, tracer)
- Tooling: UV, Ruff, mypy, pytest

## Key Paths

- Handler: `functions/src/functions/handler.py`
- Config: `functions/src/functions/config.py`
- Tests: `functions/tests/{unit,integration}`
- Infra: `sst.config.ts`

## Routes (in handler.py)

```
("GET", "/") → handle_root()
("GET", "/health") → handle_health(context)
("POST", "/echo") → handle_echo(parse_request(event))
("GET", "/time") → handle_time()
("GET", "/fetch") → handle_fetch()
("POST", "/strands") → handle_ai_query(parse_request(event))
("GET", "/error") → handle_error()
("OPTIONS", "*") → handle_options()
```

## Response Contract

- Standard envelope: `{ success: bool, timestamp: str, data?: {}, error?: str }`.
- `make_response(status, data?, error?)` sets CORS and JSON body consistently.

## Env Vars (config.py)

- `STAGE` (default `dev`), `AWS_REGION` (default `us-east-1`)
- `AWS_LAMBDA_FUNCTION_NAME` (set by Lambda)
- `BEDROCK_MODEL_ID` (default `amazon.nova-lite-v1:0`)
- `AI_TIMEOUT` (default `30` seconds)
- HTTP client timeout: `REQUEST_TIMEOUT = 10` (code-level)

## Bedrock Permissions

- Granted in `sst.config.ts`: `bedrock:Converse`, `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` for Nova.
- Change model by updating `BEDROCK_MODEL_ID` or code.

## Development Commands

- Setup: `pnpm install:all` (Node deps + `uv sync` for Python)
- Live dev: `pnpm dev` (hot reload to real Lambda, logs shown)
- Tests: `pnpm py:test` (coverage: `pnpm py:test-cov`)
- Quality: `pnpm py:lint`, `pnpm py:format`, `pnpm py:typecheck`, or `pnpm quality`

## Testing Notes

- Unit tests focus on pure handlers/utilities.
- Integration tests exercise `handler(event, context)` end-to-end.
- Mock patterns:
  - `@patch("src.functions.handler.httpx.Client")` for external HTTP
  - `@patch("src.functions.handler.Agent")` for AI calls
- Fixtures: see `functions/tests/conftest.py` (`mock_lambda_context`, events).

## Adding Endpoints

- Add a function to `handler.py` and wire it in `ROUTES`.
- Parse JSON with `parse_request(event)` for POST routes.
- Return via `make_response` to ensure envelope + CORS.
- Add tests under `functions/tests` (unit + integration where useful).

## Adding Dependencies

- Python: edit `functions/pyproject.toml` → `[project].dependencies`, then `uv sync`.
- Infra/Node: edit `package.json` if you need new SST/CDK libs.

## Infra Edits

- `sst.config.ts` controls: timeout, memory, CORS, env, permissions.
- Dev CORS is `*`; production can restrict origins via `allowOrigins`.
- Outputs: function URL (`api.url`), function name.

## AI Call Shape

- Request body: `{ "query": str, "metadata"?: {} }`.
- Handler constructs `Agent(BedrockModel(...))` and calls `agent(query)`.
- Errors: validation → 400; AI/service issues → 502; unhandled → 500.

## Style & Safety

- Keep changes narrow; follow existing patterns and names.
- Run `pnpm quality` before handing off.
- Prefer Pydantic models and small helpers; avoid over-structuring.
- Don’t introduce networked tests; mock external calls.

## Common Gotchas

- Bedrock access must be enabled in the target region/account.
- Ensure `uv sync` after changing Python deps.
- Response must be JSON-serializable; use `model_dump_json()` as done.
- Remember OPTIONS path (`*`) for CORS preflight.

