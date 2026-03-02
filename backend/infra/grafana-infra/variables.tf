variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "app_name" {
  type    = string
  default = "transinia"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "grafana_admin_user" {
  type        = string
  description = "Grafana admin username"
  default     = "admin"
}

variable "grafana_admin_password" {
  type        = string
  description = "Grafana admin password (change this!)"
  default     = "admin"
  sensitive   = true
}
