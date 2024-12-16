
variable "redis_host" {
  default     = "redis"
}

variable "redis_port" {
  type        = number
  default     = 6379
}

variable "redis_password" {
  default     = "pass12345"
}
