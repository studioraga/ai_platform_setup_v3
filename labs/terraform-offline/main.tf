terraform {
  required_version = ">= 1.6, < 2.0"
}

variable "environment" {
  description = "Practice environment name"
  type        = string
  default     = "interview"

  validation {
    condition     = contains(["dev", "test", "interview"], var.environment)
    error_message = "environment must be dev, test or interview."
  }
}

variable "replica_count" {
  description = "Number of application replicas"
  type        = number
  default     = 2

  validation {
    condition     = var.replica_count >= 1 && var.replica_count <= 5
    error_message = "replica_count must be between 1 and 5."
  }
}

locals {
  application_name = "principal-ai-${var.environment}"
}

output "application_name" {
  value = local.application_name
}

output "replica_count" {
  value = var.replica_count
}
