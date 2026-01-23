/*
  MAIN TERRAFORM CONFIGURATION
  ---------------------------
  This file defines the core Terraform settings and backend configuration
  for the S3 bucket infrastructure.
*/

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  # Resource naming
  name_prefix = "${var.app_name}-${var.env}"
  
  # S3 bucket names
  s3_bucket_raw = "${local.name_prefix}-${var.s3_bucket_raw}"
  s3_bucket_processed = "${local.name_prefix}-${var.s3_bucket_processed}"
  
  # Common tags
  common_tags = {
    Environment = var.env
    Application = var.app_name
    ManagedBy   = "Terraform"
  }
}