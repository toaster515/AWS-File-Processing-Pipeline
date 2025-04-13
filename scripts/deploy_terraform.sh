#!/bin/bash
set -e

echo "Packaging Lambda function..."

LAMBDA_DIR="src/processing"
ZIP_NAME="lambda_function.zip"
BUILD_DIR="lambda_build"

rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/python

# Install dependencies
pip install -r $LAMBDA_DIR/requirements.txt -t $BUILD_DIR/python

# Copy code
cp $LAMBDA_DIR/lambda_function.py $BUILD_DIR/
cp $LAMBDA_DIR/pdf_processor.py $BUILD_DIR/

# Zip it
cd $BUILD_DIR
zip -r ../$LAMBDA_DIR/$ZIP_NAME .
cd ../..

echo "Lambda zip ready: $LAMBDA_DIR/$ZIP_NAME"

# === Terraform apply ===
echo "Applying Terraform for Lambda, SQS, Secrets..."

cd terraform

terraform init

echo "🔍 Fetching dynamic outputs from Terraform..."
terraform apply -auto-approve -target=aws_instance.app_instance -target=aws_sqs_queue.processing_queue

# Extract outputs
OUTPUTS=$(terraform output -json)
SQS_URL=$(echo "$OUTPUTS" | jq -r .sqs_queue_url.value)
CALLBACK_URL=$(echo "$OUTPUTS" | jq -r .api_public_dns.value)

cd ..

# Regenerate processing_secrets.json
echo "Writing updated processing_secrets.json..."
cat > secrets/processing_secrets.json <<EOF
{
  "AWS_ACCESS_KEY_ID": "$AWS_ACCESS_KEY_ID",
  "AWS_SECRET_ACCESS_KEY": "$AWS_SECRET_ACCESS_KEY",
  "AWS_S3_BUCKET_NAME": "$AWS_S3_BUCKET_NAME",
  "AWS_REGION": "$AWS_REGION",
  "AWS_SQS_QUEUE_URL": "$SQS_URL",
  "API_CALLBACK_URL": "$CALLBACK_URL"
}
EOF

# Deploy remaining infrastructure
cd terraform
terraform apply \
  -target=aws_s3_bucket.lambda_deploy \
  -target=aws_s3_bucket_object.lambda_zip \
  -target=aws_secretsmanager_secret.processing_secrets \
  -target=aws_secretsmanager_secret_version.processing_secrets_version \
  -target=aws_iam_role.lambda_exec \
  -target=aws_iam_role_policy.lambda_custom_policy \
  -target=aws_iam_role_policy_attachment.lambda_basic_execution \
  -target=aws_lambda_event_source_mapping.sqs_trigger \
  -target=aws_lambda_function.pdfProcessor \
  -target=aws_sqs_queue.processing_queue \
  -auto-approve

cd ..
