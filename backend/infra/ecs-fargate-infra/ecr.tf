resource "aws_ecr_repository" "backend" {
  name         = "${local.app}-${local.env}-backend"
  force_delete = true
  tags         = local.tags
}

resource "aws_ecr_repository" "frontend" {
  name         = "${local.app}-${local.env}-frontend"
  force_delete = true
  tags         = local.tags
}
