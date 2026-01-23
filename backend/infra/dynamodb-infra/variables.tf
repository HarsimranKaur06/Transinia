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

variable "env" {
  description = "Environment (dev/prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "transinia"
}

variable "dynamodb_table_meetings_base" {
  description = "Base name for meetings table"
  type        = string
  default     = "meetings"
}

variable "dynamodb_table_actions_base" {
  description = "Base name for actions table"
  type        = string
  default     = "actions"
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
