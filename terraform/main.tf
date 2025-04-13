terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.31.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region = var.region
}

# Create landing bucket
resource "aws_s3_bucket" "landing_bucket" {
  bucket        = var.bucket_name
  force_destroy = true
  tags = {
    Name = "Landing Bucket"
  }
}

# Create IAM Role for Lambda Function
resource "aws_iam_role" "lambda_role" {
  name = "f1_racing_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Create S3 read write policy for lambda role
resource "aws_iam_policy" "s3_rw_policy" {
  name        = "s3_rw_policy"
  description = "S3 read and write permissions."
  policy      = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "ListObjectsInBucket",
        "Effect": "Allow",
        "Action": ["s3:ListBucket"],
        "Resource": ["arn:aws:s3:::${var.bucket_name}"]
      },
      {
        "Sid": "AllObjectActions",
        "Effect": "Allow",
        "Action": "s3:*Object",
        "Resource": ["arn:aws:s3:::${var.bucket_name}/*"]
      }
    ]
  }
  EOF
}

# Attach S3 read write policy for lambda role
resource "aws_iam_role_policy_attachment" "lambda_s3_rw_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_rw_policy.arn
}

# Create lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../aws_scripts/f1_racing_lambda_s3_to_rds.py"
  output_path = "${path.module}/../aws_scripts/f1_facing_lambda_s3_to_rds.zip"
}

resource "aws_lambda_function" "lambda_function" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "f1_facing_lambda_s3_to_rds"
  role          = aws_iam_role.lambda_role.arn
  handler       = "f1_facing_lambda_s3_to_rds.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime       = "python3.9"
}

# Deploy RDS instance
resource "aws_db_instance" "rds_sqlserver_db" {
  allocated_storage    = 20
  engine               = "sqlserver-ex"
  engine_version       = "15.00.4335.1.v1"
  instance_class       = "db.t3.micro"
  username             = var.rds_username
  password             = var.rds_password
  parameter_group_name = "default.sqlserver-ex-15.0"
  publicly_accessible  = true
  skip_final_snapshot  = true
}

# Create glue role
resource "aws_iam_role" "glue_role" {
  name = "f1_racing_glue_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })
}

# Create policy to give glue access to RDS database.
resource "aws_iam_policy" "glue_rds_policy" {
  name        = "glue_rds_policy"
  description = "RDS access policy for Glue job"
  policy      = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "VisualEditor0",
        "Effect": "Allow",
        "Action": [
          "rds:DescribeDBInstances",
          "rds:ExecuteStatement"
        ],
        "Resource": "${aws_db_instance.rds_sqlserver_db.arn}"
      }
    ]
  }
  EOF
}

# Attach glue rds policy to glue role
resource "aws_iam_role_policy_attachment" "glue_rds_access" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_rds_policy.arn
}

# Create lambda to glue access policy
resource "aws_iam_policy" "lambda_glue_policy" {
  name        = "f1_racing_lambda_glue_policy"
  description = "Glue access policy for Lambda function"
  policy      = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "VisualEditor0",
        "Effect": "Allow",
        "Action": [
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:BatchStopJobRun",
          "glue:GetJobRuns"
        ],
        "Resource": "*"
      }
    ]
  }
  EOF
}

# Attach lambda glue access policy to lambda role
resource "aws_iam_role_policy_attachment" "lambda_glue_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_glue_policy.arn
}

# Create glue get connection policy for testing DB connection
resource "aws_iam_policy" "glue_get_connection_policy" {
  name        = "glue_get_connection_policy"
  description = "Allows Glue to get connection for connection testing"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "glue:GetConnection",
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach glue get connection policy to glue role
resource "aws_iam_role_policy_attachment" "glue_get_connection_policy_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_get_connection_policy.arn
}

# Create EC2 access policy for glue role
resource "aws_iam_policy" "ec2_all_actions" {
  name        = "ec2_all_actions"
  description = "Allows all EC2 actions"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:*",
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach EC2 all actions policy to glue
resource "aws_iam_role_policy_attachment" "ec2_all_actions_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.ec2_all_actions.arn
}

# Create secret in AWS secrets manager
resource "aws_secretsmanager_secret" "rds_credentials" {
  name = "f1_racing_rds_credentials"
}

# Store secret content within secret
resource "aws_secretsmanager_secret_version" "example" {
  secret_id     = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode(
    {
      "username": var.rds_username,
      "password": var.rds_password,
      "hostname": var.rds_hostname,
      "port": var.rds_port,
      "dbname": var.rds_db
    }
  )
}


# Create AWS Secrets Manager access for glue role
resource "aws_iam_policy" "aws_secrets_manager" {
  name        = "glue_secrets_manager_access"
  description = "Allows access to AWS Secrets Manager"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "secretsmanager:GetSecretValue"
        ],
        "Resource": [
          aws_secretsmanager_secret.rds_credentials.arn
        ],
        "Effect": "Allow"
      }
    ]
  })
}


# Attach secrets access policy to glue role
resource "aws_iam_role_policy_attachment" "aws_secretsmanager_secret_policy_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.aws_secrets_manager.arn
}

# Attach S3 read write policy to glue role
resource "aws_iam_role_policy_attachment" "glue_s3_rw_access" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.s3_rw_policy.arn
}

resource "aws_iam_policy" "glue_service_policy" {
  name        = "glue_service_policy"
  description = "Glue permissions."
  policy      = <<-EOF
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "glue:*",
                  "s3:GetBucketLocation",
                  "s3:ListBucket",
                  "s3:ListAllMyBuckets",
                  "s3:GetBucketAcl",
                  "ec2:DescribeVpcEndpoints",
                  "ec2:DescribeRouteTables",
                  "ec2:CreateNetworkInterface",
                  "ec2:DeleteNetworkInterface",
                  "ec2:DescribeNetworkInterfaces",
                  "ec2:DescribeSecurityGroups",
                  "ec2:DescribeSubnets",
                  "ec2:DescribeVpcAttribute",
                  "iam:ListRolePolicies",
                  "iam:GetRole",
                  "iam:GetRolePolicy",
                  "cloudwatch:PutMetricData",
                  "iam:PassRole"
              ],
              "Resource": [
                  "*"
              ]
          },
          {
              "Effect": "Allow",
              "Action": [
                  "s3:CreateBucket"
              ],
              "Resource": [
                  "arn:aws:s3:::aws-glue-*"
              ]
          },
          {
              "Effect": "Allow",
              "Action": [
                  "s3:GetObject",
                  "s3:PutObject",
                  "s3:DeleteObject"
              ],
              "Resource": [
                  "arn:aws:s3:::aws-glue-*/*",
                  "arn:aws:s3:::*/*aws-glue-*/*"
              ]
          },
          {
              "Effect": "Allow",
              "Action": [
                  "s3:GetObject"
              ],
              "Resource": [
                  "arn:aws:s3:::crawler-public*",
                  "arn:aws:s3:::aws-glue-*"
              ]
          },
          {
              "Effect": "Allow",
              "Action": [
                  "logs:CreateLogGroup",
                  "logs:CreateLogStream",
                  "logs:PutLogEvents"
              ],
              "Resource": [
                  "arn:aws:logs:*:*:*:/aws-glue/*"
              ]
          },
          {
              "Effect": "Allow",
              "Action": [
                  "ec2:CreateTags",
                  "ec2:DeleteTags"
              ],
              "Condition": {
                  "ForAllValues:StringEquals": {
                      "aws:TagKeys": [
                          "aws-glue-service-resource"
                      ]
                  }
              },
              "Resource": [
                  "arn:aws:ec2:*:*:network-interface/*",
                  "arn:aws:ec2:*:*:security-group/*",
                  "arn:aws:ec2:*:*:instance/*"
              ]
          }
      ]
  }
  EOF
}

# Attach Glue service policy to glue role
resource "aws_iam_role_policy_attachment" "glue_service_access" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_service_policy.arn
}

# Create glue job
resource "aws_glue_job" "glue_write_job" {
  name     = "f1_racing_glue_s3_to_rds"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://kc-f1-racing-landing/f1_racing_glue_s3_to_rds.py"
    name            = "f1_racing_glue_s3_to_rds"
  }
}
