output "resource_group_name" {
  value       = azurerm_resource_group.this.name
  description = "Azure resource group name."
}

output "container_app_url" {
  value       = azurerm_container_app.this.latest_revision_fqdn
  description = "Container App hostname."
}
