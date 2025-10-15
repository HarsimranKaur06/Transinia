variable "allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["http://localhost:3000", "http://localhost:5000"]  # Development defaults
}