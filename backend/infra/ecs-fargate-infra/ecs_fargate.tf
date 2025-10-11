resource "aws_security_group" "tasks" {
  count = var.create_security_groups ? 1 : 0
  
  name        = "${local.app}-${local.env}-tasks-sg"
  description = "Allow ALB to reach tasks"
  vpc_id      = local.vpc_id
  tags        = local.tags

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Data source for existing security group
data "aws_security_group" "tasks" {
  count = var.create_security_groups ? 0 : 1
  
  name   = "${local.app}-${local.env}-tasks-sg"
  vpc_id = local.vpc_id
}

# Local value for security group ID
locals {
  tasks_security_group_id = var.create_security_groups ? aws_security_group.tasks[0].id : data.aws_security_group.tasks[0].id
}

# Allow ALB to connect to backend
resource "aws_security_group_rule" "alb_to_backend" {
  type                     = "ingress"
  security_group_id        = aws_security_group.tasks[0].id
  from_port                = var.backend_container_port
  to_port                  = var.backend_container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb[0].id
}

# Allow ALB to connect to frontend
resource "aws_security_group_rule" "alb_to_frontend" {
  type                     = "ingress"
  security_group_id        = aws_security_group.tasks[0].id
  from_port                = var.frontend_container_port
  to_port                  = var.frontend_container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb[0].id
}

resource "aws_ecs_cluster" "main" {
  name = "${local.app}-${local.env}-cluster"
  tags = local.tags
}

# We don't need to make the cluster conditional as it's lightweight and always needed

# Introducing a new variable to control when to fetch existing task definitions
variable "use_existing_task_definitions" {
  type        = bool
  default     = false
  description = "Whether to use existing task definitions instead of creating new ones"
}

# Data sources for task definitions
data "aws_ecs_task_definition" "backend" {
  count = (!var.create_iam_resources && var.use_existing_task_definitions) ? 1 : 0
  
  task_definition = "${local.app}-${local.env}-backend"
}

data "aws_ecs_task_definition" "frontend" {
  count = (!var.create_iam_resources && var.use_existing_task_definitions) ? 1 : 0
  
  task_definition = "${local.app}-${local.env}-frontend"
}

# Local values for task definition ARNs
locals {
  # Fallback to family name when neither creating nor using existing
  backend_task_definition_family = "${local.app}-${local.env}-backend"
  frontend_task_definition_family = "${local.app}-${local.env}-frontend"
  
  # Use ARN when available, otherwise just use family name
  backend_task_definition_arn = var.create_iam_resources ? aws_ecs_task_definition.backend[0].arn : (
    var.use_existing_task_definitions ? data.aws_ecs_task_definition.backend[0].arn : local.backend_task_definition_family
  )
  
  frontend_task_definition_arn = var.create_iam_resources ? aws_ecs_task_definition.frontend[0].arn : (
    var.use_existing_task_definitions ? data.aws_ecs_task_definition.frontend[0].arn : local.frontend_task_definition_family
  )
}

# CloudWatch log groups - using count to conditionally create
resource "aws_cloudwatch_log_group" "backend" {
  # Only create if it doesn't exist already
  count = var.create_cloudwatch_log_groups ? 1 : 0
  
  name              = "/ecs/${local.app}-${local.env}-backend"
  retention_in_days = 14
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "frontend" {
  # Only create if it doesn't exist already
  count = var.create_cloudwatch_log_groups ? 1 : 0
  
  name              = "/ecs/${local.app}-${local.env}-frontend"
  retention_in_days = 14
  tags              = local.tags
}

# Local values for CloudWatch log group names, used regardless of whether we create them
locals {
  backend_log_group_name  = "/ecs/${local.app}-${local.env}-backend"
  frontend_log_group_name = "/ecs/${local.app}-${local.env}-frontend"
}

# Task definitions
resource "aws_ecs_task_definition" "backend" {
  count = var.create_iam_resources ? 1 : 0
  
  family                   = "${local.app}-${local.env}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = local.ecs_task_execution_role_arn
  task_role_arn            = local.ecs_task_role_arn

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
          awslogs-group         = local.backend_log_group_name,
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
  count = var.create_iam_resources ? 1 : 0
  
  family                   = "${local.app}-${local.env}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = local.ecs_task_execution_role_arn
  task_role_arn            = local.ecs_task_role_arn

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
          awslogs-group         = local.frontend_log_group_name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# Services
resource "aws_ecs_service" "backend" {
  count = 1 # We don't need to make this conditional as the task definition handles IAM conditionals
  
  name             = "${local.app}-${local.env}-backend-service"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = local.backend_task_definition_arn
  desired_count    = var.backend_desired_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

  network_configuration {
    subnets          = local.private_subnet_ids
    security_groups  = [local.tasks_security_group_id]
    assign_public_ip = false
  }


  load_balancer {
    target_group_arn = local.backend_target_group_arn
    container_name   = "meeting-bot"
    container_port   = var.backend_container_port
  }

  tags       = local.tags
}

resource "aws_ecs_service" "frontend" {
  count = 1 # We don't need to make this conditional as the task definition handles IAM conditionals
  
  name             = "${local.app}-${local.env}-frontend-service"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = local.frontend_task_definition_arn
  desired_count    = var.frontend_desired_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

  network_configuration {
    subnets          = local.private_subnet_ids
    security_groups  = [local.tasks_security_group_id]
    assign_public_ip = false
  }


  load_balancer {
    target_group_arn = local.frontend_target_group_arn
    container_name   = "frontend"
    container_port   = var.frontend_container_port
  }

  tags       = local.tags
}
