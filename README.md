# SST Python AI API

Modern, minimal serverless Python API on AWS using SST v3 and Bedrock Nova models. Built as an MVP to explore Strands Agents and test AI use cases quickly and safely.

## Quick Start

```bash
# 1) Install tooling
brew install node                                 # Node.js
curl -LsSf https://astral.sh/uv/install.sh | sh   # UV for Python

# 2) Install deps (Node + Python)
pnpm setup

# 3) Start live dev (hot reload to real Lambda)
pnpm dev
# API URL appears in the terminal as apiUrl
```

## What’s Inside

- Python 3.12 Lambda (ARM64) with a single, type-safe handler
- Strands Agents + AWS Bedrock Nova integration (Nova Lite by default)
- UV-managed Python workspace, Ruff + mypy + pytest
- SST v3 dev loop with logs, tracing, and stage-aware config

## Project Structure

```
sst-python-ex/
├── sst.config.ts            # SST v3 infrastructure
├── package.json             # Unified scripts (Node + Python)
├── pyproject.toml           # UV workspace + tooling config
├── functions/
│   ├── pyproject.toml       # Python deps (Lambda)
│   ├── src/functions/
│   │   ├── handler.py       # All routes + logic
│   │   └── config.py        # Env configuration
│   └── tests/               # Unit + integration tests
```

## Configuration

- `STAGE`: deploy stage (dev, staging, production). Set by SST.
- `AWS_REGION`: AWS region (default `us-east-1`).
- `BEDROCK_MODEL_ID`: Bedrock model (default `amazon.nova-lite-v1:0`).
- `AI_TIMEOUT`: AI request timeout seconds (default `30`).
- Powertools logging env set in `sst.config.ts`.

Notes
- Dev CORS is open (`*`). Production can restrict origins.
- Bedrock access must be enabled in your account/region (Nova models).

## Endpoints

```bash
# Basic
curl "$API_URL/"                 # Welcome
curl "$API_URL/health"           # Health (Lambda context)
curl "$API_URL/time"             # UTC timestamp
curl "$API_URL/fetch"            # External httpx demo

# Echo
curl -X POST "$API_URL/echo" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "metadata": {"test": true}}'

# AI (Strands + Bedrock)
curl -X POST "$API_URL/strands" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain quantum computing simply"}'

# Error test
curl "$API_URL/error"

## Quality Commands

- lint: Biome (TS/JSON) + Ruff (Python): `pnpm lint`
- format: Biome write + Ruff fix + format: `pnpm format`
- typecheck: TypeScript + mypy: `pnpm typecheck`
- tests: Unit tests only: `pnpm test` | All tests: `pnpm test:all` | Coverage: `pnpm test:cov`
- one-shot quality: `pnpm quality`
```

Response Shape
- All responses use `{ success, timestamp, data?, error? }`.
- Errors return proper HTTP codes and a message in `error`.

## Strands + Bedrock

- Uses `strands` Agent + `BedrockModel` with Nova Lite.
- Change model via `BEDROCK_MODEL_ID` or in code.
- Required permissions (granted in `sst.config.ts`):
  - `bedrock:Converse`, `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` for Nova models.

Request Body (AI)
```json
{ "query": "Your prompt", "metadata": { "optional": "context" } }
```

## Scripts

- Dev and deploy: `pnpm aws:dev`, `pnpm aws:deploy`, `pnpm aws:remove`
- Quality: `pnpm lint`, `pnpm format`, `pnpm typecheck`, `pnpm quality`
- Tests: `pnpm test`, `pnpm test:all`, `pnpm test:cov`, `pnpm clean`
- UV direct: `uv sync`, `uv run ruff check .`, `uv run mypy functions/src`

## Testing

- Unit tests cover pure handlers and utilities.
- Integration tests exercise the full Lambda entrypoint.
- Run: `pnpm test` (coverage: `pnpm test:cov`).

## Add Features

- New endpoint
  - Add a function in `functions/src/functions/handler.py`
  - Register it in the `ROUTES` dict
  - Add tests under `functions/tests`

- New Python dependency
  - Add to `functions/pyproject.toml` → `[project].dependencies`
  - `uv sync`

- Infra changes
  - Edit `sst.config.ts` (env, permissions, memory/timeout, CORS)

## Deploy

```bash
pnpm aws:deploy                  # deploy current stage (default dev)
pnpm aws:deploy --stage staging  # deploy a different stage
pnpm aws:remove --stage dev      # remove a stage stack
```

Outputs include the public function URL (`apiUrl`).

## Troubleshooting

- Bedrock access denied: verify model access in your AWS account and region.
- CORS errors in browser: confirm allowed origins in `sst.config.ts`.
- Import errors locally: run `pnpm setup`.
- Timeouts: raise function `timeout` or lower model latency/change model.

## Roadmap Ideas

- Additional agent configs and tools, auth, DynamoDB persistence, dashboards.
