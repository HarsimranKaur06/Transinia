# Main control file for managing Terraform infrastructure creation
# This file provides a central place to control all resource creation flags

# Infrastructure Creation Control
variable "infrastructure_creation_strategy" {
  type        = string
  default     = "create_all"
  description = "Overall strategy for infrastructure creation. Valid values: create_all, use_existing, mixed"
}

# Set default values for all creation variables based on the infrastructure_creation_strategy
locals {
  # Default to creating everything
  create_all = var.infrastructure_creation_strategy == "create_all"
  
  # Default to using existing resources
  use_existing = var.infrastructure_creation_strategy == "use_existing"
  
  # Override variable defaults based on the strategy
  create_vpc_resources_default         = local.create_all ? true : false
  create_alb_resources_default         = local.create_all ? true : false
  create_iam_resources_default         = local.create_all ? true : false
  create_cloudwatch_log_groups_default = local.create_all ? true : false
  create_security_groups_default       = local.create_all ? true : false
  create_ecr_repositories_default      = local.create_all ? true : false
  
  # If using existing resources, enable data sources
  use_existing_vpc_resources_default   = local.use_existing ? true : false
  use_existing_task_definitions_default = local.use_existing ? true : false
}

# Override variables based on strategy
variable "override_creation_defaults" {
  type        = bool
  default     = false
  description = "Whether to override the defaults set by infrastructure_creation_strategy"
}

# Apply the defaults if not overriding
locals {
  create_vpc_resources         = var.override_creation_defaults ? var.create_vpc_resources : local.create_vpc_resources_default
  create_alb_resources         = var.override_creation_defaults ? var.create_alb_resources : local.create_alb_resources_default
  create_iam_resources         = var.override_creation_defaults ? var.create_iam_resources : local.create_iam_resources_default
  create_cloudwatch_log_groups = var.override_creation_defaults ? var.create_cloudwatch_log_groups : local.create_cloudwatch_log_groups_default
  create_security_groups       = var.override_creation_defaults ? var.create_security_groups : local.create_security_groups_default
  create_ecr_repositories      = var.override_creation_defaults ? var.create_ecr_repositories : local.create_ecr_repositories_default
  
  use_existing_vpc_resources   = var.override_creation_defaults ? var.use_existing_vpc_resources : local.use_existing_vpc_resources_default
  use_existing_task_definitions = var.override_creation_defaults ? var.use_existing_task_definitions : local.use_existing_task_definitions_default
}