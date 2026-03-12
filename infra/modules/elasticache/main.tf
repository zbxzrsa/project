variable "redis_node_type" {
  description = "Redis node type"
  type        = string
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
}

variable "redis_auth_token" {
  description = "Redis auth token"
  type        = string
  sensitive   = true
}

variable "subnet_ids" {
  description = "Subnet IDs"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_replication_group.redis.endpoint
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "Redis cache for AI Code Quality"
  engine                     = "redis"
  engine_version             = "7.0"
  node_type                = var.redis_node_type
  num_cache_clusters        = var.redis_num_cache_nodes
  parameter_group_name      = "default.redis7.0"
  port                      = 6379
  auth_token               = var.redis_auth_token
  security_group_ids       = var.security_group_ids
  subnet_group_name        = aws_elasticache_subnet_group.main.name
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  automatic_failover_enabled = var.redis_num_cache_nodes > 1 ? true : false
  multi_az_enabled         = var.redis_num_cache_nodes > 1 ? true : false

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}
