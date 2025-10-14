# Task execution role (pull from ECR, write logs)
resource "aws_iam_role" "ecs_task_execution" {
  count = var.create_iam_resources ? 1 : 0
  
  name               = "${local.app}-${local.env}-ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# Look up the execution role if it exists
data "aws_iam_role" "existing_ecs_task_execution" {
  count = var.create_iam_resources ? 0 : 1
  name  = "${local.app}-${local.env}-ecsTaskExecutionRole"
}

# Use either created or existing role
locals {
  ecs_task_execution_role_name = var.create_iam_resources ? aws_iam_role.ecs_task_execution[0].name : data.aws_iam_role.existing_ecs_task_execution[0].name
  ecs_task_execution_role_id   = var.create_iam_resources ? aws_iam_role.ecs_task_execution[0].id : data.aws_iam_role.existing_ecs_task_execution[0].id
  ecs_task_execution_role_arn  = var.create_iam_resources ? aws_iam_role.ecs_task_execution[0].arn : data.aws_iam_role.existing_ecs_task_execution[0].arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_attach" {
  count = var.create_iam_resources ? 1 : 0
  
  role       = local.ecs_task_execution_role_name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Add explicit CloudWatch Logs permissions for the ECS task execution role
resource "aws_iam_role_policy" "ecs_cloudwatch_logs" {
  count = var.create_iam_resources ? 1 : 0
  
  name = "${local.app}-${local.env}-cloudwatch-logs-policy"
  role = local.ecs_task_execution_role_id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${local.app}-${local.env}-backend:*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${local.app}-${local.env}-frontend:*"
        ]
      }
    ]
  })
}

# Task role (app permissions)
resource "aws_iam_role" "ecs_task_role" {
  count = var.create_iam_resources ? 1 : 0
  
  name               = "${local.app}-${local.env}-ecsTaskRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

# Look up the task role if it exists
data "aws_iam_role" "existing_ecs_task_role" {
  count = var.create_iam_resources ? 0 : 1
  name  = "${local.app}-${local.env}-ecsTaskRole"
}

# Use either created or existing role
locals {
  ecs_task_role_name = var.create_iam_resources ? aws_iam_role.ecs_task_role[0].name : data.aws_iam_role.existing_ecs_task_role[0].name
  ecs_task_role_id   = var.create_iam_resources ? aws_iam_role.ecs_task_role[0].id : data.aws_iam_role.existing_ecs_task_role[0].id
  ecs_task_role_arn  = var.create_iam_resources ? aws_iam_role.ecs_task_role[0].arn : data.aws_iam_role.existing_ecs_task_role[0].arn
}

# DynamoDB table ARNs by name (existing tables)
# We'll construct these ARNs manually to avoid dependency issues
locals {
  dynamodb_meetings_arn = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_meetings}"
  dynamodb_actions_arn = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_actions}"
}

# Least-privilege DynamoDB access
resource "aws_iam_role_policy" "task_ddb_access" {
  count = var.create_iam_resources ? 1 : 0
  
  name = "${local.app}-${local.env}-ddb-access"
  role = local.ecs_task_role_id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
      ],
      Resource = [
        local.dynamodb_meetings_arn,
        "${local.dynamodb_meetings_arn}/index/*",
        local.dynamodb_actions_arn,
        "${local.dynamodb_actions_arn}/index/*"
      ]
    }]
  })
}

# Least-privilege S3 access
locals {
  s3_raw_bucket_arn      = "arn:aws:s3:::${var.s3_bucket_raw}"
  s3_raw_bucket_objects  = "arn:aws:s3:::${var.s3_bucket_raw}/*"
  s3_proc_bucket_arn     = "arn:aws:s3:::${var.s3_bucket_processed}"
  s3_proc_bucket_objects = "arn:aws:s3:::${var.s3_bucket_processed}/*"
}

resource "aws_iam_role_policy" "task_s3_access" {
  count = var.create_iam_resources ? 1 : 0
  
  name = "${local.app}-${local.env}-s3-access"
  role = local.ecs_task_role_id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:ListBucket"],
        Resource = [local.s3_raw_bucket_arn, local.s3_proc_bucket_arn]
      },
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
        Resource = [local.s3_raw_bucket_objects, local.s3_proc_bucket_objects]
      }
    ]
  })
}
