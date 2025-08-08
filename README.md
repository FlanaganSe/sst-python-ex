# This is a hackathon project that will attempt to deploy some agents to AWS using the strands SDK, AWS Bedrock, and python AWS CDK.

# It is not intended to be a production ready project, but rather a starting point for further development.

## Setup

Instructions for setting up the development environment (macOS specific)

```bash
brew install pyenv     # Python runtime
brew install uv        # Modern version of pip for managing Python packages and environments
uv python install 3.13 # Install python v3.13

$ uv add strands-sdk                          # Install dependencies in lock file
$ uv add --dev pre-commit ruff pyright pytest # Installing dev dependencies

$ uv sync                        # Install dependencies from lock file
$ source .venv/bin/activate      # Activate virtual env

$ uv run app.py                                                        # Run the app
$ uv run ruff check .                                                  # Linter
$ uv run ruff format .                                                 # Prettier/formatter
$ uv run mypy src                                                      # Equivalent of tsc typecheck
$ uv run pytest                                                        # Run tests
$ uv run ruff check . --fix && uv run ruff format . && uv run mypy src # Run everything
```

### Structure Structure

```bash
my-strands-project/
├── .vscode/
├── pyproject.toml
├── uv.lock
├── .gitignore
├── README.md
├── .env.example
├── .env
├── src/
│   ├── __init__.py
│   ├── main.py              # entry
│   ├── config.py            # settings + env vars
│   ├── models.py            # pydantic models
│   ├── services.py          # business logic
│   └── utils.py             # helpers
└── tests/
    └── test_main.py         # basic smoke tests
```
