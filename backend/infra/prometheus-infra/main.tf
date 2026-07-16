# Data resource for ECS cluster (match Grafana)
data "aws_ecs_cluster" "main" {
  cluster_name = "${local.app}-${local.env}-cluster"
}

# Data resource for ECS task assume role policy
data "aws_iam_policy_document" "ecs_task_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}


# Data resource for main VPC (match Grafana)
data "aws_vpc" "main" {
  filter {
    name   = "tag:Application"
    values = [local.app]
  }
  filter {
    name   = "tag:Environment"
    values = [local.env]
  }
}


# Data resource for private subnets (match Grafana)
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-private-*"]
  }
}

# Data resource for ALB (match Grafana)
data "aws_lb" "main" {
  name = "${local.app}-${local.env}-alb"
}


# Data resource for ALB HTTP listener (match Grafana)
data "aws_lb_listener" "http" {
  load_balancer_arn = data.aws_lb.main.arn
  port              = 80
}
# AWS provider configuration
provider "aws" {
  region = var.aws_region
}

# Prometheus ECS/Fargate Infrastructure

locals {
  app = "transinia"
  env = terraform.workspace
  tags = {
    Project     = "transinia"
    Environment = local.env
  }
}

# IAM roles for Prometheus
resource "aws_iam_role" "prometheus_execution_role" {
  name               = "${local.app}-${local.env}-prometheus-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
  tags               = local.tags
}

resource "aws_iam_role" "prometheus_task_role" {
  name               = "${local.app}-${local.env}-prometheus-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
  tags               = local.tags
}

# Attach basic policies (logging, etc.)
resource "aws_iam_role_policy_attachment" "prometheus_execution" {
  role       = aws_iam_role.prometheus_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "prometheus_task_logs" {
  role       = aws_iam_role.prometheus_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# EFS for Prometheus config (optional, for persistence)
resource "aws_efs_file_system" "prometheus" {
  creation_token = "${local.app}-${local.env}-prometheus-efs"
  tags           = local.tags
}

resource "aws_efs_access_point" "prometheus" {
  file_system_id = aws_efs_file_system.prometheus.id
  posix_user {
    uid = 1000
    gid = 1000
  }
  root_directory {
    path = "/prometheus"
    creation_info {
      owner_uid   = 1000
      owner_gid   = 1000
      permissions = "0755"
    }
  }
  tags = local.tags
}

resource "aws_efs_mount_target" "prometheus" {
  for_each        = toset(data.aws_subnets.private.ids)
  file_system_id  = aws_efs_file_system.prometheus.id
  subnet_id       = each.value
  security_groups = [aws_security_group.efs.id]
}

# Security group for Prometheus EFS
resource "aws_security_group" "efs" {
  name        = "${local.app}-${local.env}-prometheus-efs-sg"
  description = "Allow Prometheus tasks to access Prometheus EFS"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.prometheus_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

# Security group for Prometheus
resource "aws_security_group" "prometheus_tasks" {
  name        = "${local.app}-${local.env}-prometheus-tasks-sg"
  description = "Allow Prometheus ECS tasks"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    description     = "Allow ALB to reach Prometheus"
    from_port       = 9090
    to_port         = 9090
    protocol        = "tcp"
    security_groups = data.aws_lb.main.security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "prometheus" {
  name              = "/ecs/transinia-${terraform.workspace}-prometheus"
  retention_in_days = 14
  tags              = local.tags
}

# Target group for Prometheus
resource "aws_lb_target_group" "prometheus" {
  name        = "${local.app}-${local.env}-prometheus-tg"
  port        = 9090
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.main.id
  target_type = "ip"
  health_check {
    path                = "/prometheus/-/healthy"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = local.tags
}

# ALB listener rule for Prometheus
resource "aws_lb_listener_rule" "prometheus" {
  listener_arn = data.aws_lb_listener.http.arn
  priority     = 15
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.prometheus.arn
  }
  condition {
    path_pattern {
      values = ["/prometheus", "/prometheus/*"]
    }
  }
}
