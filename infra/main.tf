terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  name_prefix = "${var.project_name}-${var.environment}"
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

module "vpc" {
  source = "./modules/vpc"

  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  project_name       = var.project_name
  environment        = var.environment
}

module "security_groups" {
  source = "./modules/security"

  vpc_id          = module.vpc.vpc_id
  project_name    = var.project_name
  environment    = var.environment
  allowed_cidr   = var.allowed_cidr
}

module "rds" {
  source = "./modules/rds"

  db_instance_class     = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name             = var.db_name
  database_username   = var.database_username
  database_password   = var.database_password
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids  = [module.security_groups.rds_sg_id]
  project_name       = var.project_name
  environment        = var.environment
}

module "elasticache" {
  source = "./modules/elasticache"

  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_auth_token     = var.redis_auth_token
  subnet_ids          = module.vpc.private_subnet_ids
  security_group_ids  = [module.security_groups.redis_sg_id]
  project_name        = var.project_name
  environment         = var.environment
}

module "alb" {
  source = "./modules/alb"

  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.public_subnet_ids
  security_group_ids = [module.security_groups.alb_sg_id]
  certificate_arn   = var.certificate_arn
  project_name     = var.project_name
  environment      = var.environment
}

module "ecs" {
  source = "./modules/ecs"

  vpc_id                 = module.vpc.vpc_id
  subnet_ids             = module.vpc.private_subnet_ids
  security_group_ids     = [module.security_groups.ecs_sg_id]
  alb_target_group_arn   = module.alb.target_group_arn
  container_image        = "${local.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_name}:latest"
  environment           = var.environment
  project_name          = var.project_name
  db_host               = module.rds.rds_endpoint
  redis_host            = module.elasticache.redis_endpoint
}

module "cloudwatch" {
  source = "./modules/cloudwatch"

  project_name  = var.project_name
  environment = var.environment
  log_group_name = "${var.project_name}-${var.environment}"
}
