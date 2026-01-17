# Justfile for frontmatter-check

set shell := ["bash", "-c"]

# List available commands
default:
    @just --list

# Install dependencies and setup pre-commit
setup:
    pip install -e ".[dev]"
    pre-commit install

# Run tests
test:
    pytest

# Run tests with coverage
coverage:
    pytest --cov=src/frontmatter_check --cov-report=term-missing

# Lint code using ruff
lint:
    ruff check .

# Format code using ruff
format:
    ruff check --fix .
    ruff format .

# Run all pre-commit hooks on all files
check:
    pre-commit run --all-files

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +

# Run the CLI tool (example usage)
run *args:
    frontmatter-check {{args}}

# Sync beads and git (session end)
sync:
    bd sync
