variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "database_username" {
  description = "Database username"
  type        = string
}

variable "database_password" {
  description = "Database password"
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

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db.instance.endpoint
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet"
  }
}

resource "aws_db_instance" "instance" {
  identifier     = "${var.project_name}-${var.environment}-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  db_name        = var.db_name
  username       = var.database_username
  password       = var.database_password
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids
  multi_az       = var.environment == "production" ? true : false
  storage_encrypted = true
  backup_retention_period = var.environment == "production" ? 7 : 1
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = "${var.project_name}-${var.environment}-finalsnapshot"

  tags = {
    Name = "${var.project_name}-${var.environment}-db"
  }
}
