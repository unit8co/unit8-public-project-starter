variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "application_name" {
  type        = string
  default     = "agentic-starter"
  description = "Application name prefix."
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Deployment environment."
}

variable "region" {
  type        = string
  default     = "europe-west1"
  description = "GCP region."
}

variable "container_image" {
  type        = string
  default     = "ghcr.io/unit8co/agentic-project-starter:latest"
  description = "Container image reference."
}

variable "container_port" {
  type        = number
  default     = 8000
  description = "Application container port."
}

variable "env_vars" {
  type        = map(string)
  default     = {}
  description = "Plain environment variables."
}

variable "secret_names" {
  type        = set(string)
  default     = ["openai-api-key"]
  description = "Secret Manager secret names."
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Extra labels."
}
