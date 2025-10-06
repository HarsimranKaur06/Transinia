resource "aws_ecr_repository" "backend" {
  name         = "transinia-backend"
  force_delete = true
  tags         = local.tags
}

resource "aws_ecr_repository" "frontend" {
  name         = "transinia-frontend"
  force_delete = true
  tags         = local.tags
}
