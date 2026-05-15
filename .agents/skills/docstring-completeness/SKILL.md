---
name: docstring-completeness
description: Ensure new or changed Python modules, classes, and public functions in this repo have concise Google-style docstrings with Args and Returns sections where applicable. Use when adding or refactoring Python code in the starter.
---

# Docstring Completeness

Use this skill when Python code changes introduce or reshape public behavior.

## Rules

- Add docstrings to public modules, public classes, and public functions.
- Keep docstrings short. State purpose first, then document the callable contract.
- Public functions and methods with parameters must include an `Args:` section.
- Public functions and methods that return a value other than `None` must include a `Returns:` section.
- Include `Raises:` only for meaningful domain errors or failure modes that callers should handle.
- Mention starter-template constraints when relevant, especially if behavior is intentionally stubbed.
- Do not add noisy docstrings to trivial private helpers unless the logic is genuinely non-obvious.

## Format

Use concise Google-style docstrings for changed public callables:

```python
def run_job(job_name: str, dry_run: bool) -> JobResult:
    """Run a registered starter job.

    Args:
        job_name: Registry name for the job to run.
        dry_run: Whether to report planned work without side effects.

    Returns:
        Structured result describing the starter job execution.
    """
```

## Checklist

- Module docstring present.
- Public API symbols documented.
- Public callable parameters are documented under `Args:`.
- Non-`None` public callable returns are documented under `Returns:`.
- Placeholder behavior is called out explicitly when relevant.
- Docstrings match actual parameter names and return values.
