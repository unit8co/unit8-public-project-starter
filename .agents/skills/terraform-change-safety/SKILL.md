---
name: terraform-change-safety
description: Make Terraform changes safely in this starter by preserving shared inputs, provider separation, formatting, and validation readiness across Azure, AWS, and GCP. Use for any infra change under infra/terraform.
---

# Terraform Change Safety

## Rules

- Keep shared naming and label logic in `modules/app_service`.
- Keep provider-specific resources inside the matching environment directory.
- Prefer explicit variables and outputs over hidden assumptions.
- Use placeholder secret wiring rather than hard-coded secrets.

## Validation

```bash
terraform fmt -recursive infra/terraform
terraform -chdir=infra/terraform/environments/<provider> init -backend=false
terraform -chdir=infra/terraform/environments/<provider> validate
```
