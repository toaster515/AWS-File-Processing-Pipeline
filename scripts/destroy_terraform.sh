#!/bin/bash
set -e

echo "Destroying all deployed AWS infrastructure..."

cd terraform

terraform destroy -auto-approve

cd ..

echo "All Terraform-managed infrastructure has been destroyed."
