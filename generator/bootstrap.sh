#!/bin/bash

set -a
source .env
set +a

aws --endpoint=http://localstack:4566 s3api create-bucket --bucket certificate-templates
aws --endpoint=http://localstack:4566 s3 cp /app/static/certificate-1-background.jpg s3://certificate-templates/static/certificate-1-background.jpg
aws --endpoint=http://localstack:4566 s3 cp /app/templates/template.html s3://certificate-templates/templates/template.html

