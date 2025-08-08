# My Python App - SST v3 Serverless Starter

A modern serverless Python application built with [SST v3](https://sst.dev) for AWS Lambda. Features live development, hot reloading, and infrastructure as code.

## 🚀 Quick Start

```bash
# Clone and install
git clone <your-repo-url>
cd my-python-app
pnpm install

# Start live development (hot reload + real AWS Lambda)
pnpm dev

# Your API will be available at:
# https://xxx.lambda-url.region.on.aws/
```

## 📋 What You Get

- **Python 3.12 Lambda** with multiple test endpoints
- **Live Development** - Changes deploy instantly to real AWS Lambda
- **Modern Python** - UV package manager, Ruff linting/formatting
- **TypeScript Infrastructure** - Type-safe AWS resource definitions
- **Event Bus** - For decoupled service communication

## 🛠️ Prerequisites

```bash
# macOS/Linux setup
brew install node          # Node.js 18+ for SST
brew install uv            # Modern Python package manager

# Configure AWS credentials
aws configure              # Or export AWS_PROFILE=your-profile
```

## 📁 Project Structure

```
my-python-app/
├── sst.config.ts          # Infrastructure definition
├── functions/             # Python Lambda functions
│   └── src/functions/
│       └── api.py         # Main API handler
├── core/                  # Shared Python code
└── packages/              # TypeScript packages (if needed)
```

## 🔌 API Endpoints

After running `pnpm dev`, test your endpoints:

```bash
# Get your API URL from the SST output, then:

curl $API_URL/              # Hello endpoint
curl $API_URL/health        # Health check with Lambda metrics
curl $API_URL/time          # Current time
curl $API_URL/test-params?foo=bar  # Query parameter testing

curl -X POST $API_URL/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'      # Echo POST body
```

## 🧰 Commands

```bash
# Development
pnpm dev                   # Start live development
pnpm deploy --stage prod   # Deploy to production
pnpm console               # Open SST management UI
pnpm remove                # Tear down stack

# Python
uv sync                    # Install Python dependencies
uv run ruff check . --fix  # Lint and fix
uv run ruff format .       # Format code
```

## 🔧 Adding Dependencies

**Python packages** - Add to `functions/pyproject.toml`:

```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.8.0",
]
```

**Node packages** - For infrastructure code:

```bash
pnpm add <package-name>
```

## 💡 Development Tips

1. **Live logs** - Watch your terminal running `pnpm dev` for real-time Lambda logs
2. **Hot reload** - Save any Python file and changes deploy in ~2 seconds
3. **Real AWS** - You're testing in actual Lambda, not a simulation
4. **Debug locally** - Add `print()` statements anywhere, they appear instantly

## 📚 Learn More

- [SST Documentation](https://docs.sst.dev)
- [SST Python Guide](https://docs.sst.dev/languages/python)
- [UV Documentation](https://docs.astral.sh/uv/)

## ⚠️ Note

This is a hackathon starter template
