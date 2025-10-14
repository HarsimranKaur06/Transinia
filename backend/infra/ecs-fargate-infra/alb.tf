resource "aws_security_group" "alb" {
  count = var.create_security_groups ? 1 : 0
  
  name        = "${local.app}-${local.env}-alb-sg"
  description = "ALB SG"
  vpc_id      = local.vpc_id
  tags        = local.tags

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Data source for existing ALB security group
data "aws_security_group" "alb" {
  count = var.create_security_groups ? 0 : 1
  
  name   = "${local.app}-${local.env}-alb-sg"
  vpc_id = local.vpc_id
}

# Local value for ALB security group ID
locals {
  # Add a fallback to prevent errors during destroy
  alb_security_group_id = try(
    var.create_security_groups ? aws_security_group.alb[0].id : data.aws_security_group.alb[0].id,
    "sg-dummy"
  )
}

resource "aws_lb" "app_alb" {
  count = var.create_alb_resources ? 1 : 0
  
  name               = "${local.app}-${local.env}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [local.alb_security_group_id]
  subnets            = local.public_subnet_ids
  tags               = local.tags
}

# Data source for existing ALB
data "aws_lb" "app_alb" {
  count = var.create_alb_resources ? 0 : 1
  
  name = "${local.app}-${local.env}-alb"
}

# Local value for ALB ARN
locals {
  app_alb_arn = var.create_alb_resources ? aws_lb.app_alb[0].arn : data.aws_lb.app_alb[0].arn
  app_alb_dns_name = var.create_alb_resources ? aws_lb.app_alb[0].dns_name : data.aws_lb.app_alb[0].dns_name
}

resource "aws_lb_target_group" "backend" {
  count = var.create_alb_resources ? 1 : 0
  
  name        = "${local.app}-${local.env}-backend-tg"
  port        = var.backend_container_port
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "ip"
  health_check {
    path    = var.backend_health_check_path
    matcher = "200-499"
  }
  tags = local.tags
}

resource "aws_lb_target_group" "frontend" {
  count = var.create_alb_resources ? 1 : 0
  
  name        = "${local.app}-${local.env}-frontend-tg"
  port        = var.frontend_container_port
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "ip"
  health_check {
    path    = var.frontend_health_check_path
    matcher = "200-499"
  }
  tags = local.tags
}

# Data sources for existing target groups
data "aws_lb_target_group" "backend" {
  count = var.create_alb_resources ? 0 : 1
  
  name = "${local.app}-${local.env}-backend-tg"
}

data "aws_lb_target_group" "frontend" {
  count = var.create_alb_resources ? 0 : 1
  
  name = "${local.app}-${local.env}-frontend-tg"
}

# Local values for target group ARNs
locals {
  backend_target_group_arn = var.create_alb_resources ? aws_lb_target_group.backend[0].arn : data.aws_lb_target_group.backend[0].arn
  frontend_target_group_arn = var.create_alb_resources ? aws_lb_target_group.frontend[0].arn : data.aws_lb_target_group.frontend[0].arn
}

resource "aws_lb_listener" "http" {
  count = var.create_alb_resources ? 1 : 0
  
  load_balancer_arn = local.app_alb_arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = local.frontend_target_group_arn
  }
}

# Data source for existing listener
data "aws_lb_listener" "http" {
  count = var.create_alb_resources ? 0 : 1
  
  load_balancer_arn = local.app_alb_arn
  port              = 80
}

# Local value for listener ARN
locals {
  http_listener_arn = var.create_alb_resources ? aws_lb_listener.http[0].arn : data.aws_lb_listener.http[0].arn
}

resource "aws_lb_listener_rule" "api" {
  count = var.create_alb_resources ? 1 : 0
  
  listener_arn = local.http_listener_arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = local.backend_target_group_arn
  }

  condition {
    path_pattern {
      values = ["/api*", "/api/*"]
    }
  }
}
