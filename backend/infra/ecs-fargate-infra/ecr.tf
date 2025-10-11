variable "create_ecr_repositories" {
  type        = bool
  default     = true
  description = "Whether to create ECR repositories or assume they already exist"
}

resource "aws_ecr_repository" "backend" {
  count = var.create_ecr_repositories ? 1 : 0
  
  name         = "transinia-backend"
  force_delete = true
  tags         = local.tags
}

resource "aws_ecr_repository" "frontend" {
  count = var.create_ecr_repositories ? 1 : 0
  
  name         = "transinia-frontend"
  force_delete = true
  tags         = local.tags
}

# Data sources for existing ECR repositories
data "aws_ecr_repository" "backend" {
  count = var.create_ecr_repositories ? 0 : 1
  
  name = "transinia-backend"
}

data "aws_ecr_repository" "frontend" {
  count = var.create_ecr_repositories ? 0 : 1
  
  name = "transinia-frontend"
}

# Local values for ECR repository references
locals {
  ecr_backend_name = var.create_ecr_repositories ? aws_ecr_repository.backend[0].name : data.aws_ecr_repository.backend[0].name
  ecr_frontend_name = var.create_ecr_repositories ? aws_ecr_repository.frontend[0].name : data.aws_ecr_repository.frontend[0].name
}
