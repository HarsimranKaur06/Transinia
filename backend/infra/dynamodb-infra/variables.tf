# variables.tf - Variables for Transinia DynamoDB resources

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key_id" {
  description = "AWS access key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret access key"
  type        = string
  sensitive   = true
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
