output "name_prefix" {
  description = "Normalized prefix shared by provider resources."
  value       = local.name_prefix
}

output "labels" {
  description = "Normalized labels or tags."
  value       = local.labels
}

output "env_vars" {
  description = "Normalized plain-text environment variables."
  value       = var.env_vars
}

output "secret_names" {
  description = "Normalized secret names."
  value       = var.secret_names
}

output "container_image" {
  description = "Normalized container image reference."
  value       = var.container_image
}

output "container_port" {
  description = "Normalized container port."
  value       = var.container_port
}

output "location" {
  description = "Normalized deployment location."
  value       = var.location
}
