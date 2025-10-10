# main.tf - Main Terraform configuration file for Transinia DynamoDB resources

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31"
    }
  }
  required_version = ">= 1.7.0"
}

provider "aws" {
  region = var.aws_region
  # Use AWS CLI configuration or environment variables instead of explicit credentials
}
