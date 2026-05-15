module "app_service" {
  source = "../../modules/app_service"

  application_name = var.application_name
  environment      = var.environment
  location         = var.location
  container_image  = var.container_image
  container_port   = var.container_port
  env_vars         = var.env_vars
  secret_names     = var.secret_names
  tags             = var.tags
}

resource "azurerm_resource_group" "this" {
  name     = "${module.app_service.name_prefix}-rg"
  location = module.app_service.location
  tags     = module.app_service.labels
}

resource "azurerm_log_analytics_workspace" "this" {
  name                = "${module.app_service.name_prefix}-law"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = module.app_service.labels
}

resource "azurerm_user_assigned_identity" "app" {
  name                = "${module.app_service.name_prefix}-identity"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = module.app_service.labels
}

resource "azurerm_container_app_environment" "this" {
  name                       = "${module.app_service.name_prefix}-env"
  location                   = azurerm_resource_group.this.location
  resource_group_name        = azurerm_resource_group.this.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.this.id
  tags                       = module.app_service.labels
}

resource "azurerm_container_app" "this" {
  name                         = module.app_service.name_prefix
  resource_group_name          = azurerm_resource_group.this.name
  container_app_environment_id = azurerm_container_app_environment.this.id
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.app.id]
  }

  template {
    min_replicas = 1
    max_replicas = 2

    container {
      name   = "api"
      image  = module.app_service.container_image
      cpu    = 0.5
      memory = "1Gi"

      dynamic "env" {
        for_each = module.app_service.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = module.app_service.secret_names
        content {
          name        = upper(replace(env.value, "-", "_"))
          secret_name = env.value
        }
      }
    }
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = module.app_service.container_port

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  dynamic "secret" {
    for_each = module.app_service.secret_names
    content {
      name  = secret.value
      value = "replace-in-key-vault-or-pipeline"
    }
  }

  tags = module.app_service.labels
}
