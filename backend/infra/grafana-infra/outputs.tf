output "grafana_url" {
  description = "Grafana URL (accessible via ALB)"
  value       = "http://${data.aws_lb.main.dns_name}/grafana"
}

output "grafana_service_name" {
  description = "Grafana ECS service name"
  value       = aws_ecs_service.grafana.name
}

output "default_credentials" {
  description = "Default Grafana credentials (CHANGE THESE!)"
  value       = "Username: ${var.grafana_admin_user}, Password: ${var.grafana_admin_password}"
  sensitive   = true
}
