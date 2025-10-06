resource "aws_security_group" "tasks" {
  name        = "${local.app}-${local.env}-tasks-sg"
  description = "Allow ALB to reach tasks"
  vpc_id      = aws_vpc.main.id
  tags        = local.tags

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Allow ALB to connect to backend
resource "aws_security_group_rule" "alb_to_backend" {
  type                     = "ingress"
  security_group_id        = aws_security_group.tasks.id
  from_port                = var.backend_container_port
  to_port                  = var.backend_container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
}

# Allow ALB to connect to frontend
resource "aws_security_group_rule" "alb_to_frontend" {
  type                     = "ingress"
  security_group_id        = aws_security_group.tasks.id
  from_port                = var.frontend_container_port
  to_port                  = var.frontend_container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_ecs_cluster" "main" {
  name = "${local.app}-${local.env}-cluster"
  tags = local.tags
}

# CloudWatch log groups
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.app}-${local.env}-backend"
  retention_in_days = 14
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${local.app}-${local.env}-frontend"
  retention_in_days = 14
  tags              = local.tags
}

# Task definitions
resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.app}-${local.env}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "meeting-bot",
      image     = var.backend_image,
      essential = true,
      portMappings = [
        { containerPort = var.backend_container_port }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      },
      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "LOG_LEVEL", value = var.log_level },
        { name = "USE_DYNAMODB", value = tostring(var.use_dynamodb) },
        { name = "DYNAMODB_TABLE_MEETINGS", value = var.dynamodb_table_meetings },
        { name = "DYNAMODB_TABLE_ACTIONS", value = var.dynamodb_table_actions },
        { name = "S3_TRANSCRIPT_BUCKET", value = var.s3_bucket_raw },
        { name = "S3_OUTPUT_BUCKET", value = var.s3_bucket_processed },
        { name = "S3_BUCKET_RAW", value = var.s3_bucket_raw },
        { name = "S3_BUCKET_PROCESSED", value = var.s3_bucket_processed }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "frontend" {
  family                   = "${local.app}-${local.env}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "frontend",
      image     = var.frontend_image,
      essential = true,
      portMappings = [
        { containerPort = var.frontend_container_port }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.frontend.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# Services
resource "aws_ecs_service" "backend" {
  name             = "${local.app}-${local.env}-backend-service"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.backend.arn
  desired_count    = var.backend_desired_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.tasks.id]
    assign_public_ip = false
  }


  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "meeting-bot"
    container_port   = var.backend_container_port
  }

  depends_on = [aws_lb_listener.http]
  tags       = local.tags
}

resource "aws_ecs_service" "frontend" {
  name             = "${local.app}-${local.env}-frontend-service"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.frontend.arn
  desired_count    = var.frontend_desired_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.tasks.id]
    assign_public_ip = false
  }


  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = var.frontend_container_port
  }

  depends_on = [aws_lb_listener.http]
  tags       = local.tags
}
