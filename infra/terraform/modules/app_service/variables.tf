variable "application_name" {
  description = "Base application name used across clouds."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "location" {
  description = "Cloud region or location."
  type        = string
}

variable "container_image" {
  description = "Container image reference."
  type        = string
}

variable "container_port" {
  description = "Application container port."
  type        = number
  default     = 8000
}

variable "env_vars" {
  description = "Plain environment variables passed to the container."
  type        = map(string)
  default     = {}
}

variable "secret_names" {
  description = "Secret names reserved for provider-native secret wiring."
  type        = set(string)
  default     = []
}

variable "tags" {
  description = "Extra labels or tags shared by all resources."
  type        = map(string)
  default     = {}
}
