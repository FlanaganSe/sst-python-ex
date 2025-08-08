# UV Python Ecosystem Guide for SST Lambda Functions

## Understanding Your Project Structure

Your project uses UV's workspace feature, which allows you to manage multiple Python packages in a single repository. Here's how it's structured:

### Root pyproject.toml (Workspace Configuration)

```toml
[tool.uv.workspace]
members = ["functions", "core"]
```

This defines a **workspace** with two member packages:

- `functions` - Contains your Lambda function code
- `core` - Contains shared/common code

### Package Structure

- **Root**: `/Users/sean.flanagan/Desktop/my-python-app/`

  - `pyproject.toml` - Workspace configuration
  - `uv.lock` - Lockfile for all packages in workspace
  - `.venv/` - Virtual environment for the entire workspace

- **functions package**: `functions/`

  - `pyproject.toml` - Package-specific dependencies
  - `src/functions/` - Python source code

- **core package**: `core/`
  - `pyproject.toml` - Package-specific dependencies
  - `src/core/` - Shared Python code

## How UV Workspaces Work

1. **Single Virtual Environment**: The entire workspace shares one `.venv` at the root
2. **Unified Lockfile**: `uv.lock` contains all dependencies from all workspace members
3. **Local Package Dependencies**: The `functions` package depends on `core` via `{ workspace = true }`

## Package Installation Process

### ✅ Correct Way to Add Dependencies

```bash
# From the workspace root, add a dependency to a specific package
uv add --package functions httpx

# Or manually edit functions/pyproject.toml and run:
uv sync
```

### ❌ Common Mistakes

```bash
# Don't do this - installs to wrong location
pip install httpx

# Don't do this - doesn't understand workspace structure
cd functions && uv add httpx
```

## Your Current Setup

After fixing your configuration, httpx is now properly installed:

### functions/pyproject.toml

```toml
dependencies = [
    "core",
    "httpx",  # ✅ Now properly added
]
```

### Python Interpreter Path

When running Python commands, always use the full path:

```bash
/Users/sean.flanagan/Desktop/my-python-app/.venv/bin/python
```

## Local Development

### Running Python Code

```bash
cd /Users/sean.flanagan/Desktop/my-python-app
/Users/sean.flanagan/Desktop/my-python-app/.venv/bin/python -m functions.src.functions.api

# Or for testing imports:
/Users/sean.flanagan/Desktop/my-python-app/.venv/bin/python -c "import httpx; print(httpx.__version__)"
```

### Installing New Packages

```bash
# Always run from workspace root
cd /Users/sean.flanagan/Desktop/my-python-app

# Add to functions package
uv add --package functions requests boto3 pydantic

# Add to core package
uv add --package core sqlalchemy

# Install dev dependencies (workspace-wide)
uv add --dev pytest black ruff
```

### Syncing Dependencies

```bash
# Run this after any pyproject.toml changes
uv sync
```

## SST Deployment

Your SST configuration now points to the correct Python handlers:

```typescript
// stacks/MyStack.ts
routes: {
  "GET /": "functions/src/functions/api.handler",
  "GET /fetch": "functions/src/functions/api.handler",  // New httpx endpoint
  // ... other routes
},
```

### Deployment Process

```bash
pnpm sst deploy
```

SST will:

1. Detect Python runtime from your handler path
2. Use UV to install dependencies in the Lambda environment
3. Bundle your `functions` and `core` packages
4. Deploy to AWS Lambda

## Example Usage

### Using httpx in Lambda Functions

```python
# functions/src/functions/handlers.py
import httpx

def handle_fetch_example(event, context):
    """Example of using httpx in Lambda."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://api.example.com/data")
            response.raise_for_status()
            return {"statusCode": 200, "body": response.json()}
    except httpx.RequestError as e:
        return {"statusCode": 503, "body": f"Network error: {e}"}
```

## Troubleshooting

### "Module not found" errors

```bash
# Check if package is installed
/Users/sean.flanagan/Desktop/my-python-app/.venv/bin/python -c "import httpx; print('OK')"

# If not, sync workspace
uv sync
```

### VS Code Python Interpreter

Set your Python interpreter to:

```
/Users/sean.flanagan/Desktop/my-python-app/.venv/bin/python
```

### Import Issues

Make sure you're importing from the correct package structure:

```python
# ✅ Correct
from functions.handlers import handle_fetch_example

# ❌ Wrong - missing package prefix
from handlers import handle_fetch_example
```

## Key Takeaways

1. **One workspace, one virtual environment** - Everything is managed at the root level
2. **Use `uv add --package <name>` syntax** - Don't install packages directly in subdirectories
3. **Always run `uv sync`** after dependency changes
4. **Use absolute Python path** for consistent execution
5. **SST handles deployment** - Just make sure your handlers are correctly referenced

## Testing Your Setup

Test the new httpx endpoint:

```bash
# After deployment
curl https://your-api-gateway-url/fetch
```

This should return a successful response showing httpx fetching data from an external API.
