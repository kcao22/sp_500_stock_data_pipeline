terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.31.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# S3 Ingress bucket
resource "aws_s3_bucket" "prod_s3_ingress_bucket" {
  bucket        = var.ingress_bucket_name
  force_destroy = true
  tags = {
    Name = "Prod S3 Ingress"
  }
}

# S3 Archive bucket
resource "aws_s3_bucket" "prod_s3_archive_bucket" {
  bucket        = var.ingress_bucket_name
  bucket_prefix = "prod_"
  force_destroy = true
  tags = {
    Name = "Prod S3 Archive"
  }
}

# Redshift serverless role for attaching policies
resource "aws_iam_role" "prod_redshift_serverless_role" {
  name = "prod_redshift_serverless_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "redshift-serverless.amazonaws.com"
        }
      },
    ]
  })
}


# Policy for Redshift serverless access to S3

resource "aws_iam_policy" "prod_s3_redshift_serverless_rw_policy" {
  name        = "prod_s3_redshift_serverless_rw_policy"
  description = "Prod Redshift serverless read and write permissions for S3."
  policy      = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "ReadObjects",
        "Effect": "Allow",
        "Action": "s3:*Object",
        "Resource": [
        "arn:aws:s3:::${var.ingress_bucket_name}/*",
        "arn:aws:s3:::${var.archive_bucket_name}/*"
        ]
      }
    ]
  }
  EOF
}


# Attach S3 access policy to prod_s3_redshift_serverless_role
resource "aws_iam_role_policy_attachment" "prod_s3_redshift_policy_attachment" {
  role       = aws_iam_role.prod_s3_redshift_role.name
  policy_arn = aws_iam_policy.prod_s3_redshift_serverless_rw_policy.arn
}


# Prod Redshift cluster
resource "aws_vpc" "prod_redshift_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "prod_redshift_subnet" {
  vpc_id                  = aws_vpc.prod_redshift_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.region
  map_public_ip_on_launch = true
}

resource "aws_security_group" "prod_redshift_sg" {
  name        = "allow-all-redshift"
  description = "Allow all inbound access"
  vpc_id      = aws_vpc.redshift_vpc.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_redshiftserverless_namespace" "prod_redshift_namespace" {
  namespace_name = "prod-redshift-namespace"
  db_name       = "prod_redw"
  default_iam_role_arn = aws_iam_role.prod_redshift_serverless_role.arn
}

resource "aws_redshiftserverless_workgroup" "prod_redshift_workgroup" {
  namespace_name    = aws_redshiftserverless_namespace.prod_redshift_namespace.namespace_name
  workgroup_name     = "prod-redshift-workgroup"
  base_capacity     = 1
  max_capacity = 2
  enhanced_vpc_routing = true
  security_group_ids = [aws_security_group.prod_redshift_sg.id]
  subnet_ids        = [aws_subnet.prod_redshift_subnet.id]
}
