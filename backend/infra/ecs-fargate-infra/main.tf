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
  app = var.app_name
  env = var.env
  tags = {
    Application = local.app
    Environment = local.env
    ManagedBy   = "Terraform"
  }
  
  # VPC and network IDs for reference by other resources
  vpc_id = aws_vpc.main.id
  public_subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]
  private_subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}
