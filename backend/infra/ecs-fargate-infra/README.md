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

## Infrastructure Creation Strategy

The Terraform configuration supports three different approaches to managing infrastructure:

1. **Create All** (default): Create all resources from scratch
2. **Use Existing**: Use existing resources (skipping creation and using data sources)
3. **Mixed**: Create some resources while using existing ones for others

### Control Variables

You can control the infrastructure creation strategy in two ways:

#### 1. High-level Strategy

Set the `infrastructure_creation_strategy` variable to one of:
- `create_all` - Create all resources
- `use_existing` - Use only existing resources 
- `mixed` - Mix of created and existing (detailed control required)

Example:
```bash
terraform apply -var="infrastructure_creation_strategy=use_existing"
```

#### 2. Granular Control

For more precise control, set individual resource creation flags:

```bash
terraform apply \
  -var="override_creation_defaults=true" \
  -var="create_vpc_resources=false" \
  -var="create_iam_resources=true" \
  -var="create_cloudwatch_log_groups=false" \
  -var="use_existing_vpc_resources=true" \
  -var="use_existing_task_definitions=true"
```

### Data Source Control

When using existing resources (`create_*=false`), you must also enable corresponding data sources (`use_existing_*=true`).

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
