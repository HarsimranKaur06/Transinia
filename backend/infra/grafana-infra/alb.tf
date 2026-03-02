# Target group for Grafana
resource "aws_lb_target_group" "grafana" {
  name        = "${local.app}-${local.env}-grafana-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/api/health"
    matcher             = "200"
  }

  tags = local.tags
}

# ALB listener rule for Grafana
resource "aws_lb_listener_rule" "grafana" {
  listener_arn = data.aws_lb_listener.http.arn
  priority     = 5

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.grafana.arn
  }

  condition {
    path_pattern {
      values = ["/grafana", "/grafana/*"]
    }
  }

  tags = local.tags
}
