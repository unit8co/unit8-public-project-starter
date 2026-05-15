# Infrastructure Layout

Terraform lives under `infra/terraform` and is split into:

- `modules/app_service`
  - common naming, tags, and normalized inputs
- `environments/azure`
  - Azure Container Apps starter deployment
- `environments/aws`
  - AWS ECS Fargate starter deployment
- `environments/gcp`
  - GCP Cloud Run starter deployment

## Design goals

- one container image interface across clouds
- environment-aware naming and tagging
- placeholder-ready secret and identity integration points
- logging and monitoring hooks present from day one

## Validation

Use Terraform commands from each environment directory:

```bash
terraform init -backend=false
terraform validate
```

Run formatting from repo root:

```bash
terraform fmt -recursive infra/terraform
```

## What remains for a real project

- replace placeholder image references
- connect real secret stores and identities
- attach real DNS, TLS, and ingress policies
- add organization-specific network guardrails
- add remote state configuration
