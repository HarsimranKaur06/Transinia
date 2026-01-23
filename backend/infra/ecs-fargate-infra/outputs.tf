output "alb_dns_name" { value = aws_lb.app_alb.dns_name }
output "cluster_name" { value = aws_ecs_cluster.main.name }
output "backend_service_name" { value = aws_ecs_service.backend.name }
output "frontend_service_name" { value = aws_ecs_service.frontend.name }
output "ecr_backend_repo" { value = aws_ecr_repository.backend.name }
output "ecr_frontend_repo" { value = aws_ecr_repository.frontend.name }
