# GitHub Secrets Setup for Grafana

## Required Secret

Add this secret to your GitHub repository:

**Secret Name:** `GRAFANA_ADMIN_PASSWORD`  
**Secret Value:** A strong password (e.g., generated with a password manager)

## How to Add the Secret

1. Go to your GitHub repository
2. Click **Settings** tab
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `GRAFANA_ADMIN_PASSWORD`
6. Value: Your strong password (min 8 characters recommended)
7. Click **Add secret**

## Security Best Practices

✅ **DO:**
- Use a strong, unique password
- Store it in a password manager
- Never commit passwords to git

❌ **DON'T:**
- Use simple passwords like "admin123"
- Share the password in plain text
- Hardcode passwords in tfvars files

## How It Works

When you push to `dev` or `master` branches:
1. GitHub Actions reads `GRAFANA_ADMIN_PASSWORD` from secrets
2. Passes it to Terraform via `-var` flag
3. Grafana container uses it as the admin password
4. Password is stored securely in ECS environment variables

## After Deployment

You can verify the secret is working by:
1. Accessing Grafana at `http://your-alb-dns/grafana`
2. Logging in with username `admin` and your secret password
3. Changing the password in Grafana UI if needed (Profile → Change password)

## Existing Secrets

Your repository should already have these secrets configured:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_ACCOUNT_ID`
- `OPENAI_API_KEY`
- `DEV_SENTRY_DSN` / `PROD_SENTRY_DSN`
- `DEV_ALB_DNS_NAME` / `PROD_ALB_DNS_NAME`
- `DEV_S3_BUCKET_RAW` / `PROD_S3_BUCKET_RAW`
- `DEV_S3_BUCKET_PROCESSED` / `PROD_S3_BUCKET_PROCESSED`
- `DEV_DYNAMODB_TABLE_MEETINGS` / `PROD_DYNAMODB_TABLE_MEETINGS`
- `DEV_DYNAMODB_TABLE_ACTIONS` / `PROD_DYNAMODB_TABLE_ACTIONS`

Just add `GRAFANA_ADMIN_PASSWORD` to this list.
