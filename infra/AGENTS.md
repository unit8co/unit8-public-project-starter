# Infra Tree Guide

## Structure Rules
- Shared naming/tagging conventions belong in `infra/terraform/modules/app_service`.
- Provider-specific resources stay inside their cloud environment directory.
- Keep Terraform examples safe for starter use: variables and placeholder IDs are fine, secrets and real credentials are not.

## Validation Rules
- Preserve `terraform fmt` clean output.
- Prefer explicit variables and outputs over hidden locals.
- Keep resource names stable and environment-aware so future users can extend rather than rewrite.
