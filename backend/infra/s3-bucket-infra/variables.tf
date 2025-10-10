/*
  TERRAFORM VARIABLES
  ------------------
  This file defines the variables used in the S3 bucket infrastructure.
*/

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  default     = "dev"
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources"
  default     = "us-east-1"
  type        = string
}

variable "s3_bucket_raw" {
  description = "Base name of S3 bucket for raw transcripts (environment will be prefixed)"
  default     = "transcripts"
  type        = string
}

variable "s3_bucket_processed" {
  description = "Base name of S3 bucket for processed outputs (environment will be prefixed)"
  default     = "outputs"
  type        = string
}

# Local variables for reuse across resources
locals {
  common_tags = {
    Environment = var.environment
    Project     = "transinia"
    ManagedBy   = "terraform"
  }
}