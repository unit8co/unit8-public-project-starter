---
name: python-quality-gates
description: "Apply the repo's Python quality bar: typed settings, small modules, Ruff-clean code, MyPy-clean interfaces, and explicit placeholder behavior. Use for any Python code contribution in this starter."
---

# Python Quality Gates

## Expectations

- Prefer typed data models over loose dictionaries at module boundaries.
- Keep imports layered: `api` and `cli` depend on `runtime` and domain services, not the reverse.
- Fail clearly on invalid registry names or missing required configuration.
- Keep starter logic honest. Stub behavior must say it is a stub.

## Validation

Run the narrowest applicable commands:

```bash
uv run ruff check .
uv run mypy src
uv run pytest
```

If you skip any command, say why.
