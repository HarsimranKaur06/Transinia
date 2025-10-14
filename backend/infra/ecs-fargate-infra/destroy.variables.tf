variable "override_creation_defaults" {
  type        = bool
  description = "Whether to override default resource creation flags"
  default     = false
}

variable "create_vpc_resources" {
  type        = bool
  description = "Whether to create VPC resources"
  default     = true
}

variable "create_alb_resources" {
  type        = bool
  description = "Whether to create ALB resources"
  default     = true
}

variable "create_iam_resources" {
  type        = bool
  description = "Whether to create IAM resources"
  default     = true
}

variable "create_cloudwatch_log_groups" {
  type        = bool
  description = "Whether to create CloudWatch Log Groups"
  default     = true
}

variable "create_security_groups" {
  type        = bool
  description = "Whether to create Security Groups"
  default     = true
}

variable "use_existing_vpc_resources" {
  type        = bool
  description = "Whether to use existing VPC resources"
  default     = false
}