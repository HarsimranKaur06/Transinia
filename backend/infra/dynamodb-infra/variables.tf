# variables.tf - Variables for Transinia DynamoDB resources

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
  description = "Name of the DynamoDB table for meetings"
  type        = string
  default     = "meeting-bot-meetings"
}

variable "dynamodb_table_actions" {
  description = "Name of the DynamoDB table for actions"
  type        = string
  default     = "meeting-bot-actions"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "Transinia"
}
