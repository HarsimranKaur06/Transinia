#!/bin/bash
# ECS Infrastructure Cleanup Script

# Set environment
ENVIRONMENT="dev"
CLUSTER_NAME="transinia-${ENVIRONMENT}-cluster"
BACKEND_SERVICE="transinia-${ENVIRONMENT}-backend-service"
FRONTEND_SERVICE="transinia-${ENVIRONMENT}-frontend-service"
REGION="us-east-1"  # Change this if your region is different

echo "Starting cleanup of ECS infrastructure for environment: ${ENVIRONMENT}"

# Check if cluster exists
CLUSTER_EXISTS=$(aws ecs describe-clusters --clusters ${CLUSTER_NAME} --query "clusters[0].status" --output text 2>/dev/null || echo "NOT_FOUND")

if [ "$CLUSTER_EXISTS" != "NOT_FOUND" ]; then
  echo "ECS Cluster ${CLUSTER_NAME} exists. Cleaning up resources..."
  
  # 1. Check and stop any running tasks
  echo "Checking for running tasks..."
  RUNNING_TASKS=$(aws ecs list-tasks --cluster ${CLUSTER_NAME} --desired-status RUNNING --query "taskArns[*]" --output text)
  
  if [ -n "$RUNNING_TASKS" ]; then
    echo "Found running tasks. Stopping them..."
    for TASK in $RUNNING_TASKS; do
      echo "Stopping task: $TASK"
      aws ecs stop-task --cluster ${CLUSTER_NAME} --task $TASK
    done
    echo "Waiting for tasks to stop..."
    sleep 10
  else
    echo "No running tasks found."
  fi
  
  # 2. Check and delete services
  echo "Checking for ECS services..."
  SERVICES=$(aws ecs list-services --cluster ${CLUSTER_NAME} --query "serviceArns" --output text)
  
  if [ -n "$SERVICES" ]; then
    echo "Found services. Updating desired count to 0..."
    for SERVICE in $SERVICES; do
      echo "Updating service: $SERVICE"
      aws ecs update-service --cluster ${CLUSTER_NAME} --service $SERVICE --desired-count 0
    done
    
    echo "Waiting for services to stabilize..."
    sleep 10
    
    echo "Deleting services..."
    for SERVICE in $SERVICES; do
      echo "Deleting service: $SERVICE"
      aws ecs delete-service --cluster ${CLUSTER_NAME} --service $SERVICE --force
    done
    
    echo "Waiting for services to be deleted..."
    sleep 20
  else
    echo "No services found."
  fi
  
  # 3. Delete the cluster
  echo "Deleting ECS cluster: ${CLUSTER_NAME}"
  aws ecs delete-cluster --cluster ${CLUSTER_NAME}
else
  echo "ECS Cluster ${CLUSTER_NAME} not found."
fi

# 4. Clean up related resources

# Check and clean up task definitions
echo "Cleaning up task definitions..."
TASK_DEFS=$(aws ecs list-task-definitions --family-prefix "transinia-${ENVIRONMENT}" --status ACTIVE --query "taskDefinitionArns" --output json)

if [ "$TASK_DEFS" != "[]" ]; then
  echo "Found task definitions. Deregistering..."
  for TASK_DEF in $(echo $TASK_DEFS | jq -r '.[]'); do
    echo "Deregistering task definition: $TASK_DEF"
    aws ecs deregister-task-definition --task-definition $TASK_DEF
  done
else
  echo "No active task definitions found."
fi

# Check and clean up CloudWatch log groups
echo "Cleaning up CloudWatch log groups..."
LOG_GROUPS=$(aws logs describe-log-groups --log-group-name-prefix "/ecs/transinia-${ENVIRONMENT}" --query "logGroups[*].logGroupName" --output json)

if [ "$LOG_GROUPS" != "[]" ]; then
  echo "Found log groups. Deleting..."
  for LOG_GROUP in $(echo $LOG_GROUPS | jq -r '.[]'); do
    echo "Deleting log group: $LOG_GROUP"
    aws logs delete-log-group --log-group-name $LOG_GROUP
  done
else
  echo "No log groups found."
fi

# Check if load balancer exists and delete if found
echo "Checking for ALB..."
ALB_NAME="transinia-${ENVIRONMENT}-alb"
ALB_ARN=$(aws elbv2 describe-load-balancers --names $ALB_NAME --query "LoadBalancers[0].LoadBalancerArn" --output text 2>/dev/null || echo "NOT_FOUND")

if [ "$ALB_ARN" != "NOT_FOUND" ]; then
  echo "Found ALB. Checking for listeners to delete..."
  LISTENERS=$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query "Listeners[*].ListenerArn" --output text)
  
  if [ -n "$LISTENERS" ]; then
    echo "Found listeners. Deleting..."
    for LISTENER in $LISTENERS; do
      echo "Deleting listener: $LISTENER"
      aws elbv2 delete-listener --listener-arn $LISTENER
    done
  fi
  
  echo "Checking for target groups..."
  TG_ARNS=$(aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN --query "TargetGroups[*].TargetGroupArn" --output text)
  
  echo "Deleting ALB: $ALB_NAME"
  aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
  
  if [ -n "$TG_ARNS" ]; then
    echo "Found target groups. Waiting for ALB to be deleted before removing target groups..."
    sleep 60
    
    echo "Deleting target groups..."
    for TG_ARN in $TG_ARNS; do
      echo "Deleting target group: $TG_ARN"
      aws elbv2 delete-target-group --target-group-arn $TG_ARN
    done
  fi
else
  echo "ALB not found."
fi

echo "ECS infrastructure cleanup complete!"