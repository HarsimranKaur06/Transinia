# Self-Hosted Grafana on ECS

Self-hosted Grafana running on your existing ECS cluster with persistent storage via EFS.

## Features

✅ No AWS SSO required - simple username/password  
✅ Persistent storage (dashboards/config saved to EFS)  
✅ Auto-connects to CloudWatch  
✅ Accessible via ALB at `/grafana`  
✅ Cost: ~$8-9/month  

## Prerequisites

**Your ECS infrastructure must be deployed first:**
```bash
cd ../ecs-fargate-infra
terraform apply -var-file='terraform.tfvars'
```

## Deployment

### Automated Deployment (Recommended)

Grafana deploys automatically via GitHub Actions when you push to `dev` or `master` branches.

**Setup GitHub Secret:**
1. Go to: Repository → Settings → Secrets and variables → Actions
2. Add secret: `GRAFANA_ADMIN_PASSWORD` with a strong password

The workflow will automatically deploy Grafana with this password.

### Manual Deployment

If deploying manually, pass the password via command line:

#### Dev Environment
```bash
cd backend/infra/grafana-infra
terraform init
terraform workspace new dev
terraform workspace select dev
terraform apply -var-file='terraform.tfvars' -var='grafana_admin_password=YOUR_STRONG_PASSWORD'
```

#### Prod Environment
```bash
terraform workspace new prod
terraform workspace select prod
terraform apply -var-file='prod.tfvars' -var='grafana_admin_password=YOUR_STRONG_PASSWORD'
```

**Note:** Never commit passwords to git. The tfvars files use "placeholder" which is overridden at deployment time.

## Access Grafana

1. **Get the URL:**
   ```bash
   terraform output grafana_url
   ```
   Example: `http://transinia-dev-alb-2104806834.us-east-1.elb.amazonaws.com/grafana`

2. **Login:**
   - Username: `admin`
   - Password: The password you set in GitHub secret `GRAFANA_ADMIN_PASSWORD`

3. **Change password immediately:**
   - Click profile icon → Change password

## Configure CloudWatch Data Source

Grafana auto-detects CloudWatch via IAM role, but you need to add it:

1. **In Grafana:** Configuration → Data Sources → Add data source
2. **Select:** CloudWatch
3. **Settings:**
   - Authentication Provider: `AWS SDK Default`
   - Default Region: `us-east-1`
   - Click "Save & Test"

## Add Sentry Data Source

1. **Get Sentry Auth Token:**
   - Sentry → Settings → Account → API → Auth Tokens
   - Create token with `org:read`, `project:read`, `event:read`

2. **In Grafana:** Configuration → Data Sources → Add data source
3. **Search:** Sentry
4. **Configure:**
   - URL: `https://sentry.io/api/0/`
   - Auth Token: (paste token)
   - Organization Slug: (from your Sentry URL)
   - Project: your project name
   - Click "Save & Test"

## Import Pre-built Dashboards

**CloudWatch Dashboards:**

1. Dashboards → Import
2. Enter Dashboard ID:
   - **ECS Monitoring**: `1077`
   - **ALB Monitoring**: `619`
   - **DynamoDB**: `2583`
3. Select CloudWatch data source
4. Click Import

## Create Custom Dashboard

**Example: Application Metrics**

```
Panel 1: API Request Rate
- Data Source: CloudWatch
- Metric: Sum of RequestCount (ALB)
- Visualization: Time series

Panel 2: Error Rate
- Data Source: Sentry
- Query: Error count by time
- Visualization: Graph

Panel 3: ECS Task CPU
- Data Source: CloudWatch
- Metric: CPUUtilization (ECS)
- Visualization: Gauge
```

## Cost Breakdown

- Fargate (0.25 vCPU, 0.5GB, 24/7): ~$7/month
- EFS storage (1GB): ~$0.30/month
- CloudWatch queries: ~$0.01/1000 metrics
- **Total: ~$8/month**

## Troubleshooting

**Can't access Grafana?**
- Check ECS service is running: `aws ecs describe-services --cluster transinia-dev-cluster --services transinia-dev-grafana-service`
- Check ALB health: Target group should show "healthy"

**CloudWatch data not showing?**
- Verify IAM role has CloudWatchReadOnlyAccess
- Check region in data source matches your resources

**Lost password?**
- Update password in tfvars
- Run: `terraform apply -var-file='terraform.tfvars'`
- Service will restart with new password

## Cleanup

```bash
terraform destroy -var-file='terraform.tfvars'  # or prod.tfvars
```

**Note:** EFS data persists even after destroy. Delete manually if needed:
```bash
aws efs delete-file-system --file-system-id <id>
```
