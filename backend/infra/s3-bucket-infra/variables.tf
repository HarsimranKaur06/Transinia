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
  description = "Name of S3 bucket for raw transcripts"
  default     = "meeting-bot-transcripts"
  type        = string
}

variable "s3_bucket_processed" {
  description = "Name of S3 bucket for processed outputs"
  default     = "meeting-bot-outputs"
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