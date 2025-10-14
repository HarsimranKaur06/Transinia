/*
  TERRAFORM VARIABLES
  ------------------
  This file defines the variables used in the S3 bucket infrastructure.
*/

variable "env" {
  description = "Environment name (e.g., dev, prod)"
  default     = "dev"
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources"
  default     = "us-east-1"
  type        = string
}

variable "app_name" {
  description = "Application name"
  default     = "transinia"
  type        = string
}

variable "s3_bucket_raw_base" {
  description = "Base name for raw transcripts bucket"
  default     = "transcripts"
  type        = string
}

variable "s3_bucket_processed_base" {
  description = "Base name for processed outputs bucket"
  default     = "outputs"
  type        = string
}

# Note: Common tags are defined in main.tf