terraform {
  backend "s3" {
    bucket         = "transinia-terraform-state"
    key            = "ecs-fargate-infra/${terraform.workspace}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
