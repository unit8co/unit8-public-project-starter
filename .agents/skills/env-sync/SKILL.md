---
name: env-sync
description: Keep environment variable names, defaults, and documentation synchronized across code, README, Docker, and Terraform examples. Use whenever runtime configuration changes.
---

# Env Sync

When you add, remove, or rename a setting, update all relevant surfaces.

## Sync Targets

- `src/agentic_project_starter/shared/config.py`
- `.env.example`
- `docs/environment-variables.md`
- `README.md`
- Docker or Terraform examples if the setting matters there

## Rule

Do not leave undocumented environment variables in starter code.
