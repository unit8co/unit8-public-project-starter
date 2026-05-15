locals {
  normalized_application_name = replace(var.application_name, "_", "-")
  name_prefix                 = "${local.normalized_application_name}-${var.environment}"

  labels = merge(
    {
      application = local.normalized_application_name
      environment = var.environment
      managed_by  = "terraform"
      starter     = "agentic-project-starter"
    },
    var.tags,
  )
}
