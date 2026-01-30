# EFS for Grafana persistent storage
resource "aws_efs_file_system" "grafana" {
  creation_token = "${local.app}-${local.env}-grafana-efs"
  encrypted      = true

  tags = merge(local.tags, {
    Name = "${local.app}-${local.env}-grafana-efs"
  })
}

resource "aws_efs_mount_target" "grafana" {
  count = length(data.aws_subnets.private.ids)

  file_system_id  = aws_efs_file_system.grafana.id
  subnet_id       = tolist(data.aws_subnets.private.ids)[count.index]
  security_groups = [aws_security_group.efs.id]
}

# Security group for EFS
resource "aws_security_group" "efs" {
  name        = "${local.app}-${local.env}-grafana-efs-sg"
  description = "Allow ECS tasks to access Grafana EFS"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.grafana_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

# Security group for Grafana tasks
resource "aws_security_group" "grafana_tasks" {
  name        = "${local.app}-${local.env}-grafana-tasks-sg"
  description = "Allow ALB to reach Grafana"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [data.aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}
