locals {
  enabled_services = toset([
    "artifactregistry.googleapis.com",
    "logging.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
  ])
}

module "app_service" {
  source = "../../modules/app_service"

  application_name = var.application_name
  environment      = var.environment
  location         = var.region
  container_image  = var.container_image
  container_port   = var.container_port
  env_vars         = var.env_vars
  secret_names     = var.secret_names
  tags             = var.tags
}

resource "google_project_service" "enabled" {
  for_each = local.enabled_services

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_service_account" "app" {
  account_id   = substr(replace(module.app_service.name_prefix, "-", ""), 0, 28)
  display_name = "${module.app_service.name_prefix} runtime"
  project      = var.project_id
}

resource "google_cloud_run_v2_service" "this" {
  name     = module.app_service.name_prefix
  location = module.app_service.location
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.app.email

    scaling {
      min_instance_count = 1
      max_instance_count = 2
    }

    containers {
      image = module.app_service.container_image

      ports {
        container_port = module.app_service.container_port
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

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
          name = upper(replace(env.value, "-", "_"))
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }
    }

    labels = module.app_service.labels
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [google_project_service.enabled]
}

resource "google_cloud_run_v2_service_iam_member" "invoker" {
  project  = google_cloud_run_v2_service.this.project
  location = google_cloud_run_v2_service.this.location
  name     = google_cloud_run_v2_service.this.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
