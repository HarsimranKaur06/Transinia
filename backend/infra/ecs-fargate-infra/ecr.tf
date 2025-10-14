resource "aws_ecr_repository" "backend" {
  name         = "${local.name_prefix}-backend"
  force_delete = true
  tags         = local.tags
}

resource "aws_ecr_repository" "frontend" {
  name         = "${local.name_prefix}-frontend"
  force_delete = true
  tags         = local.tags
}
