---
name: docstring-completeness
description: Ensure new or changed Python modules, classes, and public functions in this repo have concise docstrings that explain intent, inputs, outputs, and starter-specific constraints. Use when adding or refactoring Python code in the starter.
---

# Docstring Completeness

Use this skill when Python code changes introduce or reshape public behavior.

## Rules

- Add docstrings to public modules, public classes, and public functions.
- Keep docstrings short. State purpose first, then note important inputs or behavior.
- Mention starter-template constraints when relevant, especially if behavior is intentionally stubbed.
- Do not add noisy docstrings to trivial private helpers unless the logic is genuinely non-obvious.

## Checklist

- Module docstring present.
- Public API symbols documented.
- Placeholder behavior is called out explicitly.
- Docstrings match actual parameter names and return values.
