# Development

This project uses modern Python development tools:

- `ruff` for linting and formatting
- `mypy` for static typing
- `pytest` for unit testing

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
make install
```

## Pre-commit / Check

Before committing, run tests and linters:

```bash
make check
```
