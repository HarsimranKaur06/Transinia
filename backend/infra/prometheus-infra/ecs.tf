# ECS task definition for Prometheus
resource "aws_ecs_task_definition" "prometheus" {
  family                   = "transinia-${terraform.workspace}-prometheus"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.prometheus_execution_role.arn
  task_role_arn            = aws_iam_role.prometheus_task_role.arn

  container_definitions = jsonencode([
    {
      name       = "prometheus"
      image      = "prom/prometheus:latest"
      essential  = true
      entryPoint = ["/bin/sh", "-c"]
      command = [<<-EOT
        /bin/sh -c "
          printf '%s\n' \
            'global:' \
            '  scrape_interval: 15s' \
            'scrape_configs:' \
            '  - job_name: "prometheus"' \
            '    metrics_path: /prometheus/metrics' \
            '    static_configs:' \
            '      - targets: ["localhost:9090"]' \
            '  - job_name: "transinia-backend"' \
            '    metrics_path: /api/metrics' \
            '    static_configs:' \
            '      - targets: ["${data.aws_lb.main.dns_name}"]' \
            > /tmp/prometheus.yml && \
          exec /bin/prometheus \
            --config.file=/tmp/prometheus.yml \
            --storage.tsdb.path=/prometheus \
            --web.external-url=http://${data.aws_lb.main.dns_name}/prometheus \
            --web.route-prefix=/prometheus
        "
      EOT
      ]
      portMappings = [
        {
          containerPort = 9090
          protocol      = "tcp"
        }
      ]
      mountPoints = [
        {
          sourceVolume  = "prometheus-data"
          containerPath = "/prometheus"
          readOnly      = false
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/transinia-${terraform.workspace}-prometheus"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  volume {
    name = "prometheus-data"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.prometheus.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.prometheus.id
        iam             = "DISABLED"
      }
    }
  }

  tags = local.tags
}

# ECS service for Prometheus
resource "aws_ecs_service" "prometheus" {
  name            = "transinia-${terraform.workspace}-prometheus-service"
  cluster         = data.aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.prometheus.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.private.ids
    security_groups  = [aws_security_group.prometheus_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.prometheus.arn
    container_name   = "prometheus"
    container_port   = 9090
  }

  depends_on = [
    aws_cloudwatch_log_group.prometheus,
    aws_lb_listener_rule.prometheus,
    aws_efs_mount_target.prometheus
  ]

  tags = local.tags
}
