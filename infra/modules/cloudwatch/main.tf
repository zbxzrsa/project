variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "log_group_name" {
  description = "Log group name"
  type        = string
}

resource "aws_cloudwatch_log_group" "main" {
  name              = var.log_group_name
  retention_in_days = var.environment == "production" ? 30 : 7

  tags = {
    Name = var.log_group_name
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = "2"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/ECS"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "This metric monitors ECS CPU utilization"
  alarm_actions      = []

  tags = {
    Name = "${var.project_name}-${var.environment}-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = "2"
  metric_name        = "MemoryUtilization"
  namespace          = "AWS/ECS"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "This metric monitors ECS memory utilization"
  alarm_actions      = []

  tags = {
    Name = "${var.project_name}-${var.environment}-memory-alarm"
  }
}
