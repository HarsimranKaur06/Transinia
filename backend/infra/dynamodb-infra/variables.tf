# variables.tf - Variables for Transinia DynamoDB resources

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  default     = "dev"
  type        = string
}

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key_id" {
  description = "AWS access key ID (optional - if not provided, AWS credentials from environment or CLI config will be used)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "aws_secret_access_key" {
  description = "AWS secret access key (optional - if not provided, AWS credentials from environment or CLI config will be used)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "dynamodb_table_meetings" {
  description = "Base name of the DynamoDB table for meetings (environment will be prefixed)"
  type        = string
  default     = "meetings"
}

variable "dynamodb_table_actions" {
  description = "Base name of the DynamoDB table for actions (environment will be prefixed)"
  type        = string
  default     = "actions"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "Transinia"
}
