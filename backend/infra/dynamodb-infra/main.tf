# main.tf - Main Terraform configuration file for Transinia DynamoDB resources

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
}

locals {
  # Resource naming
  name_prefix = "${var.app_name}-${var.env}"
  
  # DynamoDB table names
  dynamodb_table_meetings = "${local.name_prefix}-${var.dynamodb_table_meetings_base}"
  dynamodb_table_actions = "${local.name_prefix}-${var.dynamodb_table_actions_base}"
  
  # Common tags
  common_tags = {
    Environment = var.env
    Application = var.app_name
    ManagedBy   = "Terraform"
  }
}
