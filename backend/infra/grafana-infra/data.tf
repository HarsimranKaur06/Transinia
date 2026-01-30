# Import existing VPC and subnets from ECS infrastructure
data "aws_vpc" "main" {
  tags = {
    Name = "${local.app}-${local.env}-vpc"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }

  tags = {
    Name = "${local.app}-${local.env}-private-*"
  }
}

data "aws_lb" "main" {
  tags = {
    Name = "${local.app}-${local.env}-alb"
  }
}

data "aws_lb_listener" "http" {
  load_balancer_arn = data.aws_lb.main.arn
  port              = 80
}

data "aws_ecs_cluster" "main" {
  cluster_name = "${local.app}-${local.env}-cluster"
}

data "aws_security_group" "alb" {
  vpc_id = data.aws_vpc.main.id

  tags = {
    Name = "${local.app}-${local.env}-alb-sg"
  }
}
