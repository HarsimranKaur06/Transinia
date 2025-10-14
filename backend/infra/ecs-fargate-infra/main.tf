terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

locals {
  # Basic info
  app = var.app_name
  env = var.env

  # Resource naming
  name_prefix = "${local.app}-${local.env}"
  
  # Constructed resource names
  s3_bucket_raw        = "${local.name_prefix}-${var.s3_bucket_raw_base}"
  s3_bucket_processed  = "${local.name_prefix}-${var.s3_bucket_processed_base}"
  dynamodb_meetings    = "${local.name_prefix}-${var.dynamodb_table_meetings_base}"
  dynamodb_actions     = "${local.name_prefix}-${var.dynamodb_table_actions_base}"
  
  # ECS resource names
  cluster_name         = "${local.name_prefix}-cluster"
  backend_service_name = "${local.name_prefix}-backend-service"
  frontend_service_name = "${local.name_prefix}-frontend-service"
  
  # Common tags
  tags = {
    Application = local.app
    Environment = local.env
    ManagedBy   = "Terraform"
  }
}
