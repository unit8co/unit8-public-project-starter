---
name: test-coverage-discipline
description: Keep test coverage aligned with starter behavior by adding or updating smoke tests for config, API, CLI, registries, and failure cases. Use when code changes could alter observable behavior.
---

# Test Coverage Discipline

## Testing Rules

- Add at least one direct test for each changed user-facing behavior.
- Cover both success and clear failure paths when registries or validation are involved.
- Prefer small smoke tests over heavy integration tests for starter scaffolding.
- When adding a new command, route, or registry entry, update tests in the same change.

## Preferred Areas

- `tests/test_api.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- registry-specific tests
