# SST Python AI API

Minimal serverless Python API on AWS using SST v3 and Bedrock Nova (via Strands Agents). Built for fast prototyping with strong tests and simple ops.

## Quick Start

```bash
# 1) Prereqs
brew pnpm                                         # pnpm (after installing node with nvm)
curl -LsSf https://astral.sh/uv/install.sh | sh   # UV for Python

# 2) Install deps (Node + Python)
pnpm setup

# 3) Live dev (hot reload to a real Lambda)
pnpm dev
# Use the Function URL printed as apiUrl (replace $API_URL below)
```

## What’s Inside

- Python 3.12 Lambda (ARM64), single handler
- Strands Agents + Bedrock Nova Lite
- UV workspace with Ruff, mypy, pytest
- SST v3 dev loop with logs and CORS

## Project Structure

```
sst-python-ex/
├── sst.config.ts            # Infra (Function + URL + perms)
├── package.json             # Scripts (Node + Python)
├── pyproject.toml           # UV workspace + tooling
├── functions/
│   ├── pyproject.toml       # Lambda Python deps
│   ├── src/functions/
│   │   ├── handler.py       # Routes + logic (entry: handler)
│   │   └── config.py        # Env config
│   └── tests/               # Unit + integration
```

## Configuration

- `STAGE`: deploy stage (SST sets)
- `AWS_REGION`: default `us-east-1`
- `BEDROCK_MODEL_ID`: default `amazon.nova-lite-v1:0`
- `AI_TIMEOUT`: default `30` seconds
- CORS, logging, and perms are set in `sst.config.ts`

## Endpoints

Replace `$API_URL` with the Function URL from `pnpm dev` output.

```bash
# Basics
curl "$API_URL/"                  # Welcome
curl "$API_URL/health"            # Health
curl "$API_URL/time"              # UTC timestamp
curl "$API_URL/fetch"             # External httpx demo

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
```

## Commands

- Dev: `pnpm dev`
- Deploy/Remove: `pnpm aws:deploy` / `pnpm aws:remove`
- Tests: `pnpm test` (unit), `pnpm test:all`, `pnpm test:cov`
- Quality: `pnpm lint`, `pnpm format`, `pnpm typecheck`, `pnpm quality`

## Response Format

- Envelope: `{ success, timestamp, data?, error? }`
- Errors return appropriate HTTP status + `error`

## Strands + Bedrock

- Uses `strands.Agent(BedrockModel(...))` with Nova Lite
- Change model via `BEDROCK_MODEL_ID` or code
- Permissions (granted in `sst.config.ts`):
  `bedrock:Converse`, `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`

### AI Request Body

```json
{ "query": "Your prompt", "metadata": { "optional": "context" } }
```

## Development

- New endpoint: add function in `handler.py` → register in `ROUTES` → add tests
- Python deps: edit `functions/pyproject.toml` → `uv sync`
- Infra: edit `sst.config.ts`

## Troubleshooting

- Enable Bedrock Nova access in your AWS account/region
- CORS in browsers: adjust `allowOrigins` in `sst.config.ts`
- Local import issues: run `pnpm setup`
- Timeouts: adjust function timeout or model choice
