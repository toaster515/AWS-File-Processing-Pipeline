#!/bin/bash
apt-get update -y
apt-get install -y docker.io awscli

systemctl start docker
systemctl enable docker

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker pull <account>.dkr.ecr.us-east-1.amazonaws.com/flask-api:latest

docker run -d -p 8000:8000 --name flask-api-container \
  -e AWS_REGION=us-east-1 \
  -e USE_AWS_SECRETS=true \
  -e AWS_SECRET_NAME=lambda/file-processing-creds \
  <account>.dkr.ecr.us-east-1.amazonaws.com/flask-api:latest
