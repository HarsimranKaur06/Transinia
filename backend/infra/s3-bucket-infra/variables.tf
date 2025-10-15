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

variable "s3_bucket_raw" {
  description = "Name for raw transcripts bucket"
  default     = "transcripts"
  type        = string
}

variable "s3_bucket_processed" {
  description = "Name for processed outputs bucket"
  default     = "outputs"
  type        = string
}

# Note: Common tags are defined in main.tf

variable "allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = [
    "http://localhost:3000",                                    # Local development frontend
    "http://localhost:5000",                                    # Local development backend
    "http://transinia-dev-alb.*.amazonaws.com",                # Dev ALB domain
    "https://transinia-dev-alb.*.amazonaws.com",               # Dev ALB domain (HTTPS)
    "http://transinia-prod-alb.*.amazonaws.com",               # Prod ALB domain
    "https://transinia-prod-alb.*.amazonaws.com"               # Prod ALB domain (HTTPS)
  ]
}