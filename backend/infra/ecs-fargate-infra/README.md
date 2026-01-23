# ECS Fargate Infra (dev)

This folder creates the AWS infrastructure for Transinia:
- VPC (public/private)
- ALB with path rules (`/api/*` -> backend, others -> frontend)
- ECS Fargate cluster + 2 services
- CloudWatch log groups
- ECR repos
- IAM task roles with access to your existing S3 buckets and DynamoDB tables

## Prereqs
- AWS CLI configured to target the right account/region
- Terraform >= 1.5

## Run
```bash
terraform init
terraform apply -auto-approve
```
Then copy outputs:
- `alb_dns_name`, `cluster_name`, `backend_service_name`, `frontend_service_name`, `ecr_backend_repo`, `ecr_frontend_repo`

## Hook up CI
In GitHub → Settings → Secrets and variables → Actions:
- `AWS_REGION` (e.g., us-east-1)
- `AWS_ACCOUNT_ID`
- `CLUSTER_NAME` (from outputs)
- `BACKEND_SERVICE` (from outputs)
- `FRONTEND_SERVICE` (from outputs)
- `BACKEND_PUBLIC_URL_DEV` = `http://<alb_dns_name>/api`

Your workflow then builds/pushes images and deploys to these services.
