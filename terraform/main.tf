terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
  required_version = ">= 0.14.9"
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Environment = "FOSS4G"
      Owner       = "James Santucci"
      Project     = "GroundWork HITL RV Workflow"
    }
  }
}