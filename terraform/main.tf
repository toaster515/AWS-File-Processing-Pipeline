
provider "aws" {
  region = var.aws_region
}

resource "aws_lambda_function" "pdfProcessor" {
  function_name = "pdfProcessor"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"

  s3_bucket = aws_s3_bucket.lambda_deploy.bucket
  s3_key    = aws_s3_bucket_object.lambda_zip.key
  role      = aws_iam_role.lambda_exec.arn

  timeout      = 60
  memory_size  = 1024

  environment {
    variables = {
      AWS_REGION      = var.aws_region
      AWS_SECRET_NAME = "lambda/file-processing-creds"
    }
  }
}

resource "aws_s3_bucket" "lambda_deploy" {
  bucket = var.s3_bucket
  force_destroy = true
}

resource "aws_s3_bucket_object" "lambda_zip" {
  bucket = aws_s3_bucket.lambda_deploy.bucket
  key    = "lambda/pdf_processor.zip"
  source = "../src/processing/lambda_function.zip"
  etag   = filemd5("../src/processing/lambda_function.zip")
}

resource "aws_secretsmanager_secret" "processing_secrets" {
  name = "lambda/file-processing-creds"
}

resource "aws_secretsmanager_secret_version" "processing_secrets_version" {
  secret_id     = aws_secretsmanager_secret.processing_secrets.id
  secret_string = file("./secrets/processing_secrets.json")
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_custom_policy" {
  name = "lambda_secrets_s3_sqs_access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
          "s3:GetObject",
          "s3:PutObject",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_sqs_queue" "processing_queue" {
  name = "pdf-processing-queue"
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.processing_queue.arn
  function_name = aws_lambda_function.pdfProcessor.function_name
  batch_size       = 1
  enabled          = true
}

# === EC2 App Deployment ===
resource "aws_security_group" "app_sg" {
  name        = "app-sg"
  description = "Allow HTTP and SSH"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app_instance" {
  ami           = var.ec2_ami
  instance_type = var.ec2_instance_type
  key_name      = var.key_name
  subnet_id     = var.subnet_id
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = file("./scripts/user_data.sh")

  tags = {
    Name = "flask-api-app"
  }
}

output "sqs_queue_url" {
  value = aws_sqs_queue.processing_queue.id
}

output "api_public_dns" {
  value = "http://${aws_instance.app_instance.public_dns}:8000/api/records/"
}