terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Local variables for consistent naming
locals {
  app  = var.app_name
  env  = var.env
  tags = {
    Application = var.app_name
    Environment = var.env
    ManagedBy   = "Terraform"
  }
}
