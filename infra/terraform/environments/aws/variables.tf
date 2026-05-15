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
  default     = "eu-central-1"
  description = "AWS region."
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

variable "desired_count" {
  type        = number
  default     = 1
  description = "ECS service desired task count."
}

variable "cpu" {
  type        = number
  default     = 512
  description = "Fargate CPU units."
}

variable "memory" {
  type        = number
  default     = 1024
  description = "Fargate memory in MiB."
}

variable "env_vars" {
  type        = map(string)
  default     = {}
  description = "Plain environment variables."
}

variable "secret_names" {
  type        = set(string)
  default     = ["openai-api-key"]
  description = "Secrets Manager secret names."
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Extra AWS tags."
}
