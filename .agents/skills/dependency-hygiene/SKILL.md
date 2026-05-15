---
name: dependency-hygiene
description: Keep Python dependencies lean and intentional in this starter. Use when adding, upgrading, or removing packages in pyproject.toml, Docker, or CI.
---

# Dependency Hygiene

## Rules

- Every new dependency must justify a real starter capability.
- Prefer a small number of well-scoped libraries over overlapping toolchains.
- Keep runtime and dev dependencies separated.
- Update lockfile, Docker install path, and CI commands together.

## Review Questions

- Is this dependency required for the starter itself, or only for one project that may use it later?
- Can the same outcome be achieved with an existing dependency?
