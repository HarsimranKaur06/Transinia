output "alb_dns_name" { value = local.app_alb_dns_name }
output "cluster_name" { value = aws_ecs_cluster.main.name }
output "backend_service_name" { value = aws_ecs_service.backend[0].name }
output "frontend_service_name" { value = aws_ecs_service.frontend[0].name }
output "ecr_backend_repo" { value = local.ecr_backend_name }
output "ecr_frontend_repo" { value = local.ecr_frontend_name }
